## Cloud storage simulator

In this repo, interaction of clients and servers of adaptive video streaming is simulated. 
The goal is to estimate the number of users that can be handled by a server, allowing the service provider to anticipate the need for additional resources.

### Simulation model

The system definition is such that its simulated results should be as close to the real world dynamics as possible, 
for this the traces of users’ statistics from real world services are used to provide realistic values for session 
duration and round-trip-times (RTTs). Other parameters such as offered bitrates and video segment values are taken 
from the most popular streaming service, YouTube. The system is modelled using three main components, 
which are the server, the client and the network. Parameters used to model each component are given below,

- Server:

  Offered video segment size (S) = 3 seconds (recommended by YouTube), server download capacity = 15 Gbps and server output buffer size = 160 Mb

- Client:

  Playout buffer size = 10 segments, client access capacity = [3Mb, 6Mb, 9Mb, 12Mb and 20Mb] from given traces, client patience time = 30 seconds 
  for general purpose; and varies from 5 seconds to 40 seconds in 8 steps of 5 seconds when iterating over different patience values. 
  And, the client requests for a new segment as soon as it starts playback of a current segment.

- Network:

  Network model is simplified by accounting for only three types of delays, server delay, propagation delay and client access delay, 
  all of which can be calculated from above mentioned parameters. Only thing to be considered is that the clients may abandon service in two cases, 
  + when video start-up delay is too high
  + when there has been a long video-stall due to empty playout buffer at client side

### Simulation results

<img width="650" alt="image" src="https://user-images.githubusercontent.com/25234772/220393140-e73e25be-a78d-4f62-ba69-ef0235509de4.png">

<img width="650" alt="image" src="https://user-images.githubusercontent.com/25234772/220393228-cc442a68-3d13-481c-a463-0af20a46edab.png">

<img width="650" alt="image" src="https://user-images.githubusercontent.com/25234772/220393389-5e089bda-d9f6-4928-83f1-31c1f0da673d.png">

<img width="650" alt="image" src="https://user-images.githubusercontent.com/25234772/220393450-efe93e20-de1f-4374-a6db-cdb09bb78b5f.png">

<img width="650" alt="image" src="https://user-images.githubusercontent.com/25234772/220393504-ad6fb799-ab6f-4452-bfed-44d65cdb7ec3.png">

<img width="650" alt="image" src="https://user-images.githubusercontent.com/25234772/220393228-cc442a68-3d13-481c-a463-0af20a46edab.png">
