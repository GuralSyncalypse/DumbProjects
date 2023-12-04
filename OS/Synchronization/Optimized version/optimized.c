#include "philosopher.h"

unsigned int RNG(unsigned int seed)
{
    srand(seed);
    unsigned int number = 2000 + rand() % (2000 + 1); // [2000, 4000]
    return number;
}

void eat(const unsigned int id, DWORD eat_time)
{
    max_dine_time[id]--;

    printf("Philosopher %d is eating.\n", id);
    Sleep(eat_time);
}

void think(const unsigned int id, DWORD think_time)
{
    printf("Philosopher %d is thinking.\n", id);
    Sleep(think_time);
}

void take_chopsticks(int left_chopstick, int right_chopstick)
{
    bool success = false;

    // Breaking Hold and Wait.
    while(!success){
        pthread_mutex_lock(&chopsticks[left_chopstick]);

        // pthread_mutex_trylock return -1 if fail.
        if(pthread_mutex_trylock(&chopsticks[right_chopstick]) != 0){
            pthread_mutex_unlock(&chopsticks[left_chopstick]);
        }
        else success = true;
    }
}

void return_chopsticks(int left_chopstick, int right_chopstick)
{
    pthread_mutex_unlock(&chopsticks[right_chopstick]);
    pthread_mutex_unlock(&chopsticks[left_chopstick]);
}

void swap_chopsticks(int *left_chopstick, int *right_chopstick)
{
    int temp = *left_chopstick;
    *left_chopstick = *right_chopstick;
    *right_chopstick = temp;
}

void *dining(void *arg)
{
    int id = *(int *)arg;
    int left_chopstick = id;
    int right_chopstick = (id + 1) % MAX_PHILOSOPHERS;

    if(left_chopstick > right_chopstick) swap_chopsticks(&left_chopstick, &right_chopstick); // Imposing Order.
    while(max_dine_time[id] > 0){
        unsigned int seed = pthread_self() * max_dine_time[id];
        DWORD time = RNG(seed);

        // Limiting Access.
        sem_wait(&can_sit);
        take_chopsticks(left_chopstick, right_chopstick);
        sem_post(&can_sit);
        
        // Critical section.
        eat(id, time);

        return_chopsticks(left_chopstick, right_chopstick);

        // Remainder section.
        time = RNG(time);
        think(id, time);
    }
    printf("\t\t\t[Philosopher %d has left.]\n", id);
}