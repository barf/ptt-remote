# About
PTT-button network remote-control for VATSIM audio with modular simulator systems.

Sends PTT button presses over TCP/IP (using ZeroMQ) to a Windows PC/VM running the Audio for VATSIM client. 

by barf <stuart@macintosh.nz>

# Requirements
* Windows PC/VM (with headset attached, running Audio for VATSIM client)
  * Install [Python 3](https://www.python.org/downloads/windows/)
    * Install Python module ZeroMQ: `python -m pip install zmq`
    * Install Python module Numpy: `python -m pip install numpy`
  * Install [vJoystick](https://sourceforge.net/projects/vjoystick/)
* X-Plane/simulator box with PTT button attached
  * Requires Python 3
    * Install Python module PyGame: `python -m pip install pygame`
    * Install Python module ZeroMQ: `python -m pip install zmq`

# Usage
On the Windows PC/VM running the Audio for VATSIM client:
1. Install Python 3 and vJoystick.
1. Attach your headset, or patch/route the audio.
1. Run (double-click on) `ptt_remote_rx.py`
1. Allow receiving on port TCP/5555 in the Windows firewall. The default port can be changed by editing the `ptt_remote_rx.py` file.

On the X-Plane/simulator box with PTT button:
1. Execute `ptt_remote_tx.py <host> <port>` with the TCP/IP address (or FQDN) and port of the host running `ptt_remote_rx.py`. The default port is 5555.

The buttons on USB HID devices attached to the simulator should now be mapped to the first virtual joystick device. 
To test if buttons are being mapped use the vJoystick `JoyMonitor.exe` tool.

# Troubleshooting
If there is no connection, you may need to add an exception to the Windows Firewall: 
https://blogs.msdn.microsoft.com/mandi/2014/11/03/how-to-create-a-windows-firewall-inbound-rule/

If `ptt_remote_rx.py` does not run, check that Python 3 and the required Python modules are correctly installed.
