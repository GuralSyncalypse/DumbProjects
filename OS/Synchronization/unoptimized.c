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
    pthread_mutex_lock(&chopsticks[left_chopstick]);
    pthread_mutex_lock(&chopsticks[right_chopstick]);
}

void return_chopsticks(int left_chopstick, int right_chopstick)
{
    pthread_mutex_unlock(&chopsticks[right_chopstick]);
    pthread_mutex_unlock(&chopsticks[left_chopstick]);
}

void *dining(void *arg)
{
    int id = *(int *)arg;
    int left_chopstick = id;
    int right_chopstick = (id + 1) % MAX_PHILOSOPHERS;

    while(max_dine_time[id] > 0){
        unsigned int seed = pthread_self() * max_dine_time[id];
        DWORD time = RNG(seed);
        take_chopsticks(left_chopstick, right_chopstick);
        
        // Critical section.
        eat(id, time);

        return_chopsticks(left_chopstick, right_chopstick);

        // Remainder section.
        time = RNG(time);
        think(id, time);
    }
    printf("\t\t\t[Philosopher %d has left.]\n", id);
}