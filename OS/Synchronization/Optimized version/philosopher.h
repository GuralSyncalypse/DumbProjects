#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include <semaphore.h>
#include <time.h>
#include <windows.h>

#ifndef __PHILOSOPHER__
#define __PHILOSOPHER__

#define MAX_PHILOSOPHERS 5
static unsigned int max_dine_time[MAX_PHILOSOPHERS] = {5, 5, 5, 5, 5};
static pthread_mutex_t chopsticks[MAX_PHILOSOPHERS]; // Binary Semaphores.
static sem_t can_sit; // Counting Semaphore.

void eat(const unsigned int id, DWORD eat_time);
void think(const unsigned int id, DWORD eat_time);
void take_chopsticks(int left_chopstick, int right_chopstick);
void return_chopsticks(int left_chopstick, int right_chopstick);
void *dining(void *arg);

#endif
