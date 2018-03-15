# date: 14 march 2018
# author: haroonr
library(ggplot2)
#library(data.table)
setwd('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/Writings/UoS/plots/')
root <- '/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/AD_gridsearch_results.csv'

df = read.csv(root)
colnames(df) <- c('home','appliance','context_no','alpha','sigma','precision','recall','fscore')

df_context = df[df$alpha == 2 & df$sigma == 2.5,]
keep <- c('home','context_no','fscore')
df_sub <- df_context[keep]
df_long = reshape2::melt(df_sub,id.vars=c('home','context_no'))
ggplot(data=df_long,aes(context_no,value,color=home)) + geom_line()


df_alpha = df[df$context_no == 4 & df$sigma == 2.5,]
keep <- c('home','alpha','fscore')
df_sub <- df_alpha[keep]
df_long = reshape2::melt(df_sub,id.vars=c('home','alpha'))
ggplot(data=df_long,aes(alpha,value,color=home)) + geom_line()


df_sigma = df[df$context_no == 4 & df$alpha == 2,]
keep <- c('home','sigma','fscore')
df_sub <- df_sigma[keep]
df_long = reshape2::melt(df_sub,id.vars=c('home','sigma'))
ggplot(data=df_long,aes(sigma,value,color=home)) + geom_line()