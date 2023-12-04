#include "philosopher.h"

// Main.
void menu()
{
    printf("\t\t\t+--------The Dining of Philosophers--------+\n");
    printf("\t\t\t|0. Exit.                                  |\n");
    printf("\t\t\t|1. Start dining.                          |\n");
    printf("\t\t\t|2. Modify dine time of each Philosopher.  |\n");
    printf("\t\t\t+------------------------------------------+> ");
}

bool run()
{
    menu();
    int option = 0;
    scanf("%d", &option);
    system("cls");

    switch(option){
        case 0: return false;
        case 1: {
            pthread_t philosophers[MAX_PHILOSOPHERS];
            int id[MAX_PHILOSOPHERS];
            
            for(int i = 0; i < MAX_PHILOSOPHERS; i++){
                id[i] = i;
                pthread_create(&philosophers[i], NULL, dining, &id[i]);
            }

            // Join up all threads to main thread.
            for(int i = 0; i < MAX_PHILOSOPHERS; i++){
                pthread_join(philosophers[i], NULL);
            }
            break;
        }
        case 2: {
            for(int i = 0; i < MAX_PHILOSOPHERS; i++){
                printf("[Current dine time of Philosopher %d: %d.]\n", i, max_dine_time[i]);
                printf("Philosopher %d> ", i);
                scanf("%d", &max_dine_time[i]);
            }
            break;
        }
        default: printf("[This option does not exist.]\n");
    }
    return true;
}

int main(int argc, char **argv)
{
    bool process = true;
    while(process){
        process = run();
    }

    printf("[End Program.]\n");
    return EXIT_SUCCESS;
}