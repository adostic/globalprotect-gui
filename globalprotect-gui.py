#!/usr/bin/python3
import os
import sys
import threading
import gi
import time

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator

lock = threading.Lock()
monitor_status = False


def run_continuously(indicator, interval=3):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                if monitor_status:
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
    status = set_icon_thread_function(indicator)
    if status:
        global monitor_status
        monitor_status = True
    cease_continuous_run = run_continuously(indicator)

    indicator.set_menu(menu())
    gtk.main()
    cease_continuous_run.set()


def set_icon_thread_function(indicator):
    status, icon = get_gp_status()
    indicator.set_icon(icon)
    return status


def get_gp_status():
    lock.acquire()
    stream = os.popen('globalprotect show --status')
    output = stream.read()
    lock.release()
    if output.find("Connected") != -1:
        return True, os.path.join(sys.path[0], "network-vpn-symbolic-green.svg")
    return False, os.path.join(sys.path[0], "network-vpn-no-route-symbolic-red.svg")


def menu():
    menu = gtk.Menu()

    command_monitor = gtk.MenuItem('Monitor')
    command_monitor.connect('activate', monitor)
    menu.append(command_monitor)

    command_connect = gtk.MenuItem('Connect')
    command_connect.connect('activate', connect)
    menu.append(command_connect)

    command_disconnect = gtk.MenuItem('Disconnect')
    command_disconnect.connect('activate', disconnect)
    menu.append(command_disconnect)

    command_details = gtk.MenuItem('Details')
    command_details.connect('activate', details)
    menu.append(command_details)

    command_about = gtk.MenuItem('About')
    command_about.connect('activate', about)
    menu.append(command_about)

    exit_tray = gtk.MenuItem('Close')
    exit_tray.connect('activate', quit_trey)
    menu.append(exit_tray)

    menu.show_all()

    return menu


def monitor(_):
    global monitor_status
    monitor_status = True


def disconnect(_):
    run_command("globalprotect disconnect")


def connect(_):
    global monitor_status
    monitor_status = True
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
    main()
