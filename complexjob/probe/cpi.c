#include "mpi.h" 
#include <stdio.h> 
#include <math.h> 

int main( int argc, char *argv[] ) 
{ 
    int n_intervals = 16384;
    int n, myid, numprocs, i; 
    double PI25DT = 3.141592653589793238462643; 
    double mypi, pi, h, sum, x; 
    double startwtime, endwtime;

    MPI_Init(&argc,&argv); 
    MPI_Comm_size(MPI_COMM_WORLD,&numprocs); 
    MPI_Comm_rank(MPI_COMM_WORLD,&myid); 
    n = n_intervals;
    if (myid == 0) {
    	printf("Using %d processes\n", numprocs);      
        startwtime = MPI_Wtime(); 
    }
    MPI_Bcast(&n, 1, MPI_INT, 0, MPI_COMM_WORLD); 

    h   = 1.0 / (double) n; 
    sum = 0.0; 
    for (i = myid + 1; i <= n; i += numprocs) { 
        x = h * ((double)i - 0.5); 
        sum += (4.0 / (1.0 + x*x)); 
    } 
    mypi = h * sum; 
    MPI_Reduce(&mypi, &pi, 1, MPI_DOUBLE, MPI_SUM, 0, 
           MPI_COMM_WORLD); 

    if (myid == 0)  {
        endwtime = MPI_Wtime();
        printf("pi is approximately %.16f, Error is %.16f\n", 
                   pi, fabs(pi - PI25DT)); 
        printf("wall clock time = %f\n", endwtime-startwtime);      
  
    } 
    MPI_Finalize(); 
    return 0; 
}
