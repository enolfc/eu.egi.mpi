#include <stdio.h>
#include <mpi.h>

#define process_A 0
#define process_B 1
#define ping 100
#define pong 101

#define number_of_messages 50
#define start_length 8
#define length_faktor 64
#define max_length 2097152     /* 2 Mega */
#define number_package_sizes 4

int main(int argc, char **argv) {
    int my_rank;
    int np;
    int err = 0;
 
    int i, j;  
    int length_of_message;    
    double start, finish, time, transfer_time; 
    MPI_Status status;
    float buffer[max_length];

    MPI_Init(&argc, &argv);

    MPI_Comm_size(MPI_COMM_WORLD,&np);

    if (np > 1) { 
        MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);

        if (my_rank == process_A) {
            length_of_message = start_length; 
            printf("message size\t\ttransfertime\t\tbandwidth\n"); 
            for (i = 1; i <= number_package_sizes; i++) { 
                start = MPI_Wtime();

                for (j = 1; j <= number_of_messages; j++) {
                    MPI_Send(buffer, length_of_message, MPI_FLOAT, process_B, 
                            ping, MPI_COMM_WORLD);

                    MPI_Recv(buffer, length_of_message, MPI_FLOAT, process_B, 
                            pong, MPI_COMM_WORLD, &status);
                }

                finish = MPI_Wtime();

                time = finish - start;

                transfer_time = time / (2 * number_of_messages);

                printf("%i bytes\t\t%f sec\t\t%f MB/s\n", 
                        length_of_message*sizeof(float),
                        transfer_time,
                        1.0e-6*length_of_message*sizeof(float) / transfer_time);

                length_of_message *= length_faktor;
            }
        }
        else if (my_rank == process_B) {
            length_of_message = start_length;

            for (i = 1; i <= number_package_sizes; i++) {    
                for (j = 1; j <= number_of_messages; j++) {
                    MPI_Recv(buffer, length_of_message, MPI_FLOAT, process_A, 
                            ping, MPI_COMM_WORLD, &status);

                    MPI_Send(buffer, length_of_message, MPI_FLOAT, process_A, 
                            pong, MPI_COMM_WORLD);
                }  
                length_of_message *= length_faktor;
            }
        }
    } else {
        printf("Only one processor, exiting.\n"); 
        err = 7;
    }
    MPI_Finalize();
    return err;
}

