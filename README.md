# About
PTT button network remote-control for VATSIM audio
by barf <stuart@macintosh.nz>

# Requirements
* Windows PC/VM running Audio for VATSIM client
  * Install [Python 3](https://www.python.org/downloads/windows/)
    * Install Python module ZeroMQ `python -m pip install zmq`
    * Install Python module Numpy `python -m pip install numpy`
  * Install [vJoystick](https://sourceforge.net/projects/vjoystick/)
* Windows/GNU/Linux/Mac simulator with yoke/stick/PTT button attached
  * Requires Python 3
    * uses Python module `python -m pip install pygame`
    * uses Python module `python -m pip install zmq`

# Usage
On the Windows PC/VM running the Audio for VATSIM client:
1. Install Python 3 and vJoystick
1. Attach your headset (or patch/route the audio) to the Windows PC/VM.
1. Run (double-click on) `ptt_remote_rx.py`

On the simulator box with PTT button:
1. Execute `ptt_remote_tx.py <host> <port>` with the host TCP/IP address (or FQDN) and port.
