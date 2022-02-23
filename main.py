import pandas as pd
import seaborn as sns
from scipy import stats
import numpy as np
import matplotlib as plt
# Read the csv data sets (I saved a csv file with only 2020 GDP data and loaded it directly)
Netflix = pd.read_csv("data/netflix price in different countries.csv")
GDP2020 = pd.read_csv("data/GDP_2020.csv")
# Remove the data of the countries that are not common in the two data sets
GDP2020_2 = GDP2020[GDP2020["country"].isin(Netflix["Country"])]
Netflix_2 = Netflix[Netflix["Country"].isin(GDP2020_2["country"])]
# Remove the unnecesarry data from the data sets (Film and series per country in the Netflix data for example)
# Thereafter sort the data by country in lexical order
# (I do not know if that is the right word for sorting by letters)
GDP2020_2 = pd.DataFrame({"Country" : GDP2020_2["country"], "GDP":GDP2020_2["gdp"]}).sort_values("Country")
Netflix_2 = pd.DataFrame({"Country" : Netflix_2["Country"],
                          "Netflix Basic":Netflix_2["Cost Per Month - Basic ($)"],
                          "Netflix Standard":Netflix_2["Cost Per Month - Standard ($)"],
                          "Netflix Premium":Netflix_2["Cost Per Month - Premium ($)"]}).sort_values("Country")
# Do not really know. I think this code is not needed anymore
Netflix_2.set_index("Country")
GDP2020_2.set_index("Country")

# Merge the GDP and Netflix data for each country
End = pd.merge(GDP2020_2, Netflix_2, on="Country")
# Melt the data set by subscription type (This is used to make the combined scatter plot)
End_2 = End.melt(id_vars=["Country", "GDP"], value_vars=["Netflix Basic", "Netflix Standard", "Netflix Premium"],
                 var_name="Subscription Type", value_name="Subscription Price")

# Remove the outliers in the GDP (Most likely only removed the USA. Their GDP is huge)
# Stack Overflow link for outlier removal:
# https://stackoverflow.com/questions/23199796/detect-and-exclude-outliers-in-a-pandas-dataframe
End_3 = End_2[(np.abs(stats.zscore(End_2["GDP"]))) < 3]
End_4 = End[(np.abs(stats.zscore(End["GDP"]))) < 3]

# Plot combined scatter plot
Plot = sns.scatterplot(data=End_3, x="GDP", y="Subscription Price", hue="Subscription Type")
plt.pyplot.show()
# Plot individual scatter plots
Plot8 = sns.relplot(data=End_3, x="GDP", y="Subscription Price", hue="Subscription Type", col="Subscription Type", legend=False)
plt.pyplot.show()
# Plot a very big plot with many different plots inside
Plot9 = sns.pairplot(data=End_4)
plt.pyplot.show()

#Plot2 = sns.lmplot(data=End_4, x="GDP", y="Netflix Basic")
#plt.pyplot.show()

#Plot3 = sns.lmplot(data=End_4, x="GDP", y="Netflix Standard")
#plt.pyplot.show()

#Plot4 = sns.regplot(data=End_4, x="GDP", y="Netflix Premium")
#plt.pyplot.show()

# Calculate Pearson correlation and plot its heatmap
Corr = End_4.corr()
Plot5 = sns.heatmap(Corr, vmin=-1, vmax=1, center=0, annot=True, cmap="seismic",
                    xticklabels=["GDP", "Basic", "Standard", "Premium"],
                    yticklabels=["GDP", "Basic", "Standard", "Premium"])
plt.pyplot.show()
# Calculate Kendall correlation and plot its heatmap
Corr2 = End_4.corr(method="kendall")
Plot6 = sns.heatmap(Corr2, vmin=-1, vmax=1, center=0, annot=True, cmap="seismic",
                    xticklabels=["GDP", "Basic", "Standard", "Premium"],
                    yticklabels=["GDP", "Basic", "Standard", "Premium"])
plt.pyplot.show()
# Calculate Spearman correlation and plot its heatmap
Corr3 = End_4.corr(method="spearman")
Plot7 = sns.heatmap(Corr3, vmin=-1, vmax=1, center=0, annot=True, cmap="seismic",
                    xticklabels=["GDP", "Basic", "Standard", "Premium"],
                    yticklabels=["GDP", "Basic", "Standard", "Premium"])
plt.pyplot.show()

# Save the different plots
Plot.get_figure().savefig("Figures/Scatter_AllData.png")
Plot5.get_figure().savefig("Figures/Correlation_Pearson.png")
Plot6.get_figure().savefig("Figures/Correlation_Kendall.png")
Plot7.get_figure().savefig("Figures/Correlation_Spearman.png")
Plot8.fig.savefig("Figures/Scatter_Individual.png")


