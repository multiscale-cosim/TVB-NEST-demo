

NEURON	{
  ARTIFICIAL_CELL mpi_input
  RANGE interval, number, start, time_synch
  THREADSAFE : if APCount.record uses distinct instances of Vector
}

PARAMETER {
	interval	= 10 (ms) <1e-9,1e9>: time between spikes (msec)
	number	= 10 <0,1e9>	: number of spikes (independent of noise)
	start		= 50 (ms)	: start of first spike
	time_synch = 20 (ms): time of synchronization
}

ASSIGNED {
nb_spikes
id
}

VERBATIM
#include <mpi.h>
#include <string.h>
#include <stdbool.h>
static MPI_Comm comm;
static int count_id = 1;
ENDVERBATIM
INITIAL {
	net_send(0, 3)
	VERBATIM
	if (id == 0 ){
		id = count_id;
		count_id +=1;
	}
	ENDVERBATIM
}

DESTRUCTOR {
		VERBATIM
    	if (id == 1){
			bool value[ 1 ] = { true };
			MPI_Send( value, 1, MPI_CXX_BOOL, 0, 0, comm );
			MPI_Barrier(comm);
			MPI_Comm_disconnect( &comm );
    	}
		ENDVERBATIM
}

VERBATIM
double spikes_time[100];
static int get_spikes(_threadargsprotocomma_ double _lt) {
	// printf("########################################  network get spike %f %d\n",_lt,(int)id);
	bool value[ 1 ] = { true };
	MPI_Send( value, 1, MPI_CXX_BOOL, 0, (int)id, comm );
	// Receive the size of data
    MPI_Status status_mpi;
	// Receive the size of the data in total and for each devices
	int value_int [1] = {0};
    MPI_Recv( value_int, 1 , MPI_INT, MPI_ANY_SOURCE, (int)id, comm, &status_mpi );
	nb_spikes = value_int[0];
	// printf("########################################  network size %f %d \n",nb_spikes,value_int[0]);
    // Receive the data
    MPI_Recv( spikes_time, nb_spikes, MPI_DOUBLE, status_mpi.MPI_SOURCE, (int)id, comm, &status_mpi );
}
ENDVERBATIM

NET_RECEIVE (w) {
	if (flag == 0) { : external event
	net_send(0, 1)
	}
	if (flag == 3) { : from INITIAL
		net_send(0, 2) : get first data
	}
	if (flag == 2) {
		LOCAL a,i
		get_spikes(t)
		i = 0
		while (i < nb_spikes){
			VERBATIM
			_la = spikes_time[(int)_li];
			ENDVERBATIM
			:printf("########################################  network send %f \n",a)
			net_event(a)
			net_send(a, 1)
			i = i + 1
		}
		net_send(time_synch, 2)
	}
	if (flag == 1) {
		net_event(t)
	}
}

VERBATIM


char *path;
char port_name[10000];

void get_port(char* path, char* port_name )
	{
	// path of the file : path+label+id+.txt
	// (file contains only one line with name of the port)
	FILE *fp;
	// add the id of the device to the path
    fp = fopen(path, "r");

	// read the file
	fscanf(fp, "%s", port_name);
	fclose(fp);
	}

void preparation_MPI(){
	printf("preparation MPI \n");
    // Create the connection with MPI
    // 1) take all the ports of the connections
    // get port and update the list of device only for master
    // add the link between MPI communicator and the device (devices can share the same MPI communicator)
    get_port(path, port_name);
	printf("%s\n",port_name);
    MPI_Comm_connect(port_name,
                     MPI_INFO_NULL,
                     0,
                     MPI_COMM_WORLD,
                     &comm); // should use the status for handle error
}
ENDVERBATIM

FUNCTION set_path(){
VERBATIM
	if (id == 0 ){
		id = count_id;
		count_id +=1;
	}
	if (id != 1){
		//printf("################ not path _id %d  ",(int)id);
		return _lset_path;
	}
	path = hoc_gargstr(1);
	printf("path %s",path);
ENDVERBATIM
	preparation_MPI()
}

