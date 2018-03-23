# Distributed Blackboard - Centralized communication version

* Each post is sent to the leader which distributes it to the network

* The leader should be able to handle correctly multiple posts from different nodes

## Leader Election
* Use the Ring-based Election Algorithm when starting the board in order to decide the leader

  * Find your neighbor (e.g. the node with the next IP number)
  
  * Every node should send only to their next neighbor
  
  * Use a locally generated random number as a criterion for selecting the leader (e.g. highest wins)
  
* The protocol stars running as soon as the nodes are up

## After the election

* The leader is established and everyone agrees on it

* After the election, nodes send new entries directly to the leader (no ring any more)

* The leader can serve as a centralized sequencer:

  * It decides the correct, global order of all messages
  
  * Everybody else follows that order

## Task 1: Leader Election https://youtu.be/uZ1dUuqmLRE

* Explain the leader election algorithm

* Use a field in the webpage to show who the leader is and what its random number is

* Discuss the solution cost of the leader election algorithm that you use

## Task 2: Blackboard (centralized) https://youtu.be/pXDPXjdESoM

* Show that concurrent submissions do not lead to problems anymore

  * all blackboard entries always appear in the same order
  
* Demonstrate the cost of your solution (i.e. cost of a post delivered to all nodes)

* Briefly discuss pros and cons of this design
