Note: Normal distributions will be written in the form N(mean, stddiv)
Note2: This program is run through Pycharm with Anaconda environment. Therefore, iPython is heavily used in running this program
	(Hence why there is no main function).

This test run was made by running 1000 rounds where each round generates 100 sample. The objects used in the test are:
- RNG1 which includes 4 random variables:
	- W = Z + X + N(0, 10)
	- X = N(100, 10)
	- Y = N(50, 5)
	- Z = 0.5X + Y
- RNG2 which includes 6 random variables:
	- U = N(100, 10)
	- V = N(100, 20)
	- W = V + 2U
	- X = W + U^2
	- Y = V^2 + N(0, 1000)
	- Z = U^2 + V^2

The program runs in rounds. In the test each round the objects generate 100 samples according to their random variables
Then after generating the samples the Pearson correlations between all random variables are calculated using all generated samples
Thereafter the calculated correlation coefficients are added to their own lists so that they can be used to make plots

The object has a method to check if the correlations are reaching a stable rate (Convergance)
This method takes the latest 5 correlations and measures deviation between them
(Quite hard to explain in writing without it becoming too long)

In this test a deviation of 0.0005 was checked for, and all correlation coefficients did not exceed that deviation.

The resulting plots and data can be found in the folders Data and Figures.

This is just a brief explanation. The plan is to explain everything in a meeting.