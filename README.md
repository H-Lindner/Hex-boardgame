# Hex-boardgame

First bigger programming project. This project was part of a highschool seminar in 2018/19. The final grade was a 14 out of 15.

We were not allowed to use any external libraries and had to use tkinter for any graphics. Accordingly, all the shapes are "hand drawn".

It was recommended to use simple decision tree algorithms for the AI. However, since this approach doesn't really work in Hex due to the large amount of possible moves,
I wrote a Monte Carlo algorithm. It essentially tried every possible, then finished a certain amount of games with random moves, and then played the move with the most wins.
This approach was serviceable, but poorly optimized and therefore too resource intensive to calculate beyond a single move.  
