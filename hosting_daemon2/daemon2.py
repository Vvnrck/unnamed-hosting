import sys
import settings
import sched
import scenarios


def periodic(scheduler, interval, action, actionargs=()):
    action(*actionargs)
    scheduler.enter(interval, 1, periodic,
                    (scheduler, interval, action, actionargs))
  
    
def seconds(t):
    return t


def minutes(t):
    return 60 * seconds(t)

    
def hours(t):
    return 60 * minutes(t)


if __name__ == '__main__':
    scenarios.start_apps()

    scheduler = sched.scheduler()
    periodic(scheduler, seconds(30), scenarios.deploy_apps)
    periodic(scheduler, seconds(30), scenarios.disable_apps)
    periodic(scheduler, seconds(30), scenarios.enable_apps)
    periodic(scheduler, minutes(10), scenarios.revisit_running_apps)
    scheduler.run()

