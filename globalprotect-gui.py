import os
import sys
import threading
import gi
import time

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator

lock = threading.Lock()
verbose = False


def run_continuously(indicator, interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                set_icon_thread_function(indicator)
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.daemon = True
    continuous_thread.start()
    return cease_continuous_run


def main():
    indicator = appindicator.Indicator.new("customtray",
                                           os.path.join(sys.path[0], "network-vpn-no-route-symbolic-red.svg"),
                                           appindicator.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    set_icon_thread_function(indicator)
    cease_continuous_run = run_continuously(indicator)

    indicator.set_menu(menu())
    gtk.main()
    cease_continuous_run.set()


def set_icon_thread_function(indicator):
    icon = get_gp_status()
    indicator.set_icon(icon)


def log(output):
    if verbose:
        print(output)


def get_gp_status():
    if is_interface_up("gpd0"):
        return os.path.join(sys.path[0], "network-vpn-symbolic-green.svg")
    return os.path.join(sys.path[0], "network-vpn-no-route-symbolic-red.svg")


def is_interface_up(interface):
    try:
        with open('/sys/class/net/' + interface + '/operstate') as f:
            content = f.read()
            if 'down' in content:
                return False
            else:
                return True
    except:
        return False


def menu():
    gtk_menu = gtk.Menu()

    command_connect = gtk.MenuItem('Connect')
    command_connect.connect('activate', connect)
    gtk_menu.append(command_connect)

    command_disconnect = gtk.MenuItem('Disconnect')
    command_disconnect.connect('activate', disconnect)
    gtk_menu.append(command_disconnect)

    command_details = gtk.MenuItem('Details')
    command_details.connect('activate', details)
    gtk_menu.append(command_details)

    command_about = gtk.MenuItem('About')
    command_about.connect('activate', about)
    gtk_menu.append(command_about)

    exit_tray = gtk.MenuItem('Close')
    exit_tray.connect('activate', quit_trey)
    gtk_menu.append(exit_tray)

    gtk_menu.show_all()

    return gtk_menu


def disconnect(_):
    run_command("globalprotect disconnect")


def connect(_):
    run_command('xterm -e globalprotect connect')


def details(_):
    run_command('xterm -e "globalprotect show --details;read"')


def about(_):
    license_path = os.path.join(sys.path[0], "LICENSE")
    readme_path = os.path.join(sys.path[0], "README.md")
    run_command('xterm -e "cat ' + license_path + '; echo ; cat ' + readme_path + ';read"')


def run_command(command):
    lock.acquire()
    os.system(command)
    lock.release()


def quit_trey(_):
    gtk.main_quit()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--verbose':
        verbose = True
    main()
