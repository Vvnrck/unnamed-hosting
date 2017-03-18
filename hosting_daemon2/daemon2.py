import sys
import settings
import sched
import scenaries


def periodic(scheduler, interval, action, actionargs=()):
    scheduler.enter(interval, 1, periodic,
                    (scheduler, interval, action, actionargs))
    action(*actionargs)
    
    
def seconds(t):
    return t


def minutes(t):
    return 60 * seconds(t)

    
def hours(t):
    return 60 * minutes(t)


if __name__ == '__main__':
    scheduler = sched.scheduler()
    periodic(scheduler, seconds(20), scenaries.deploy_apps)
    periodic(scheduler, seconds(20), scenaries.disable_apps)
    periodic(scheduler, seconds(20), scenaries.enable_apps)
    periodic(scheduler, minutes(10), scenaries.revisit_running_apps)
    scheduler.run()

