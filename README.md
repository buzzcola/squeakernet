## SqueakerNet FLP
#### the ultimate feline lifestyle platform

squeakernet brings together (or will bring together) the internet of things (IoT), blockchain 
and deep learning to create an immersive experiential platform for cats and other mammals.

as of right now it:
- dispenses cat food on a schedule
- hosts a simple web server with remote feed, stats, logs and a feeding chart
- weighs the cat's bowl to measure food dispensed and monitor feeding habits
- audio system praises and encourages cats during meal time

https://youtu.be/f9sUizPjpKM
https://youtu.be/koqxneu9SLM
https://www.instagram.com/p/Bl_AyjBFyaL/
https://www.instagram.com/p/BmBhocHgJdD/

    .       .         
    \`-"'"-'/
     } 6 6 {    
    =.  Y  ,=   
      /^^^\  .
     /     \  )           
jgs (  )-(  )/ 
     ""   ""

dedicated to mr. squeakers, r.i.p.

yet to come:
- email/text me an alarm when the hopper is empty
- tweet about the cats dietary habits each day

setup:
  sudo apt-get install libttspico-utils

  pip install wiringpi
  pip install RPi.GPIO
  pip install bottle
  pip install psutil

adjust squeakernet.ini for your rig
configure cronjobs for the web server and scheduled feeding. example:

# take weight reading once a minute, offset 30 seconds to avoid feed time
* * * * * ( sleep 30 ; python /share/squeakernet/squeakernet.py logweight )

# morning feed at 7:00am
0 7 * * * python /share/squeakernet/squeakernet.py feed

# evening feed at 7:00pm
0 19 * * * python /share/squeakernet/squeakernet.py feed

# log startup, start the web server on boot
@reboot python /share/squeakernet/squeakernet.py writelog 'Squeakernet was rebooted.'
@reboot python /share/squeakernet/squeakernet_web.py
