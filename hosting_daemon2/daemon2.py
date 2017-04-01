import sys
import settings
import sched
import signal
import scenarios


def periodic(scheduler, interval, action, actionargs=()):
    action(*actionargs)
    scheduler.enter(interval, 1, periodic,
                    (scheduler, interval, action, actionargs))
  
    
def seconds(t): return t
def minutes(t): return 60 * seconds(t)
def hours(t): return 60 * minutes(t)
    
    
def main():
    scenarios.start_apps()
    scheduler = sched.scheduler()
    periodic(scheduler, seconds(30), scenarios.deploy_apps)
    periodic(scheduler, seconds(30), scenarios.disable_apps)
    periodic(scheduler, seconds(30), scenarios.enable_apps)
    periodic(scheduler, minutes(10), scenarios.revisit_running_apps)
    scheduler.run()


if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    
    def exit_gracefully(signum, frame):
        signal.signal(signal.SIGINT, original_sigint)
        try:
            scenarios.shut_down_gracefully()
            exit(0)
        except KeyboardInterrupt:
            sys.exit(1)  
        signal.signal(signal.SIGINT, exit_gracefully)
    
    signal.signal(signal.SIGINT, exit_gracefully)
    main()
