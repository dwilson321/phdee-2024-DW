import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from OLS import manualOLS


datapath = r'C:\Users\Owner\Dropbox\Personal\Enviro Econ II\phdee-2023-DW\homework2\data'
outputpath = r'C:\Users\Owner\Dropbox\Personal\Enviro Econ II\phdee-2023-DW\homework2\output'

'''
------------------------------------------------------------------------------
Q1.1: Difference in means
------------------------------------------------------------------------------
'''

kwh=pd.read_csv(datapath +'/kwh.csv')

retro=kwh.loc[kwh['retrofit']==1].drop('retrofit',axis=1)
noretro=kwh.loc[kwh['retrofit']==0].drop('retrofit',axis=1)

# Generate a table of means and standard deviations for the observed variables (there are faster ways to do this that are less general)
## Generate means and standard deviations
means_control = noretro.mean()
stdev_control = noretro.std()
nobs_control = pd.Series(noretro.count().min())

means_treatment_1 = retro.mean()
stdev_treatment = retro.std()
nobs_treatment = pd.Series(retro.count().min())

## Compute P-values and t-statistics
p_vals = []
t_stats = []    
for col in retro.columns:
    p_vals.append(stats.ttest_ind(noretro[col],retro[col],)[1])
    t_stats.append(stats.ttest_ind(noretro[col],retro[col],)[0])
p_vals = pd.Series(p_vals, index = retro.columns)
t_stats = pd.Series(t_stats, index = retro.columns)

## Set the row and column names
rownames = pd.concat([pd.Series(['Monthly electricity consumption (kWh)','Square feet of home','Outdoor average temperature (\\textdegree F)', 'Observations']),
                    pd.Series([' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list to make room for stdevs

## Format means and standard deviations to two decimal places
means_control = means_control.map('{:.2f}'.format)
stdev_control = stdev_control.map('({:.2f})'.format)
nobs_control = nobs_control.map('{:.0f}'.format)

means_treatment = means_treatment_1.map('{:.2f}'.format)
stdev_treatment = stdev_treatment.map('({:.2f})'.format)
nobs_treatment = nobs_treatment.map('{:.0f}'.format)

p_vals = p_vals.map('{:.3f}'.format)
t_stats = t_stats.map('[{:.3f}]'.format)

## Align std deviations under means and add observations
col1 = pd.concat([means_control,stdev_control,nobs_control],axis = 1).stack()
col2 = pd.concat([means_treatment,stdev_treatment,nobs_treatment],axis = 1).stack()
col3 = pd.concat([p_vals,t_stats,pd.Series([' '])],axis = 1).stack()

## Add column and row labels.  Convert to dataframe (helps when you export it)
col = pd.DataFrame({'Control': col1, 'Treatment': col2, 'P-value': col3})
col.index = rownames
col.to_latex(outputpath + '/table/table1.tex',column_format='lccc',escape=False)


'''
------------------------------------------------------------------------------
Q1.2: Graphical Evidence
------------------------------------------------------------------------------
'''
fig = sns.kdeplot(retro['electricity'], color="r")
fig = sns.kdeplot(noretro['electricity'], color="b")
plt.xlabel('Monthly electricity consumption (kWh)')
plt.legend(labels = ['Retrofit','No retrofit'],loc = 'best')
plt.show
plt.savefig(outputpath + '/figure/kdensity.pdf',format='pdf')

'''
------------------------------------------------------------------------------
Q1.3: OLS by hand
------------------------------------------------------------------------------
'''

# Run with Dylan's data for Non-robust standard errors
ols1=manualOLS(kwh[['retrofit','sqft','temp']],kwh['electricity'],method='byhand')
ols1.report()

ols2=manualOLS(kwh[['retrofit','sqft','temp']],kwh['electricity'],method='statsmodels')
ols2.report()

ols3=manualOLS(kwh[['retrofit','sqft','temp']],kwh['electricity'],method='leastsquares')
ols3.report()

## Compute estimates and standard errors by
b_1 = ols1.beta().flatten()
se_1 = ols1.beta_std().flatten()
mse_1=ols1.MSE()
b_1 = pd.Series(b_1, index = ['retrofit','sqft','temp','cons']).map('{:.3f}'.format)
se_1 = pd.Series(se_1, index = ['retrofit','sqft','temp','cons']).map('({:.3f})'.format)
mse_1=pd.Series(mse_1).map('{:.3f}'.format)


## Compute estimates and standard errors
b_2 = ols2.beta().flatten()
se_2 = ols2.beta_std().flatten()
mse_2=ols2.MSE()
b_2 = pd.Series(b_2, index = ['retrofit','sqft','temp','cons']).map('{:.3f}'.format)
se_2 = pd.Series(se_2, index = ['retrofit','sqft','temp','cons']).map('({:.3f})'.format)
mse_2=pd.Series(mse_2).map('{:.3f}'.format)

## Compute estimates and standard errors
b_3 = ols3.beta().flatten()
se_3 = ols3.beta_std().flatten()
mse_3=ols3.MSE()
b_3 = pd.Series(b_3, index = ['retrofit','sqft','temp','cons']).map('{:.3f}'.format)
se_3 = pd.Series(se_3, index = ['retrofit','sqft','temp','cons']).map('({:.3f})'.format)
mse_3=pd.Series(mse_3).map('{:.3f}'.format)

## Set the row and column names
rownames = pd.concat([pd.Series(['=1 if house received retrofit','Square feet of home','Outdoor average temperature (\\textdegree F)','Constant','M.S.E.']),
                    pd.Series([' ',' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list to make room for stdevs

## Align std deviations under means and add observations
col1 = pd.concat([b_1,se_1,mse_1],axis = 1).stack()
col2 = pd.concat([b_2,se_2,mse_2],axis = 1).stack()
col3 = pd.concat([b_3,se_3,mse_3],axis = 1).stack()

## Add column and row labels.  Convert to dataframe (helps when you export it)
col = pd.DataFrame({'By Hand': col1, 'Stats Model': col1, 'Least Squares': col3})
col.index = rownames
col.to_latex(outputpath + '/table/ols.tex',column_format='lccc',escape=False)

# Run with Dylan's data for Heteroscedasticity robust standard errors
ols1=manualOLS(kwh[['retrofit','sqft','temp']],kwh['electricity'],method='byhand',useRobust=True)
ols1.report()

ols2=manualOLS(kwh[['retrofit','sqft','temp']],kwh['electricity'],method='statsmodels',useRobust=True)  
ols2.report()

ols3=manualOLS(kwh[['retrofit','sqft','temp']],kwh['electricity'],method='leastsquares',useRobust=True)
ols3.report()

## Compute estimates and standard errors by
b_1 = ols1.beta().flatten()
se_1 = ols1.beta_std().flatten()
mse_1=ols1.MSE()
b_1 = pd.Series(b_1, index = ['retrofit','sqft','temp','cons']).map('{:.3f}'.format)
se_1 = pd.Series(se_1, index = ['retrofit','sqft','temp','cons']).map('({:.3f})'.format)
mse_1=pd.Series(mse_1).map('{:.3f}'.format)

## Compute estimates and standard errors
b_2 = ols2.beta().flatten()
se_2 = ols2.beta_std().flatten()
mse_2=ols2.MSE()
b_2 = pd.Series(b_2, index = ['retrofit','sqft','temp','cons']).map('{:.3f}'.format)
se_2 = pd.Series(se_2, index = ['retrofit','sqft','temp','cons']).map('({:.3f})'.format)
mse_2=pd.Series(mse_2).map('{:.3f}'.format)

## Compute estimates and standard errors
b_3 = ols3.beta().flatten()
se_3 = ols3.beta_std().flatten()
mse_3=ols3.MSE()
b_3 = pd.Series(b_3, index = ['retrofit','sqft','temp','cons']).map('{:.3f}'.format)
se_3 = pd.Series(se_3, index = ['retrofit','sqft','temp','cons']).map('({:.3f})'.format)
mse_3=pd.Series(mse_3).map('{:.3f}'.format)

## Set the row and column names
rownames = pd.concat([pd.Series(['=1 if house received retrofit','Square feet of home','Outdoor average temperature (\\textdegree F)','Constant','MSE']),
                    pd.Series([' ',' ',' ',' '])],axis = 1).stack() # Note this stacks an empty list to make room for stdevs

## Align std deviations under means and add observations
col1 = pd.concat([b_1,se_1,mse_1],axis = 1).stack()
col2 = pd.concat([b_2,se_2,mse_2],axis = 1).stack()
col3 = pd.concat([b_3,se_3,mse_3],axis = 1).stack()

## Add column and row labels.  Convert to dataframe (helps when you export it)
col = pd.DataFrame({'By Hand': col1, 'Stats Model': col2, 'Least Squares': col3})
col.index = rownames
col.to_latex(outputpath + '/table/ols_robust.tex',column_format='lccc',escape=False)