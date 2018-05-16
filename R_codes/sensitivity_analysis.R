# date: 14 march 2018
# author: haroonr
library(Cairo)
library(ggplot2)
#library(data.table)
setwd('/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/paper_draft/paper_plots/')
#root <- '/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/AD_gridsearch_results.csv'
root <- '/Volumes/MacintoshHD2/Users/haroonr/Dropbox/UniOfStra/AD/AD_gridsearch_results_sshmm.csv'

df = read.csv(root)
colnames(df) <- c('home','appliance','context_no','alpha','sigma','precision','recall','fscore')

df_context = df[df$alpha == 2 & df$sigma == 2.5,]
keep <- c('home','context_no','fscore')
df_sub <- df_context[keep]
df_sub <- na.omit(df_sub)
#library(plyr)
#df_sub$context_no = mapvalues(df_sub$context_no,from = c(1,2,3,4,6,8), to = c(24,12,8,6,4,3))
df_long = reshape2::melt(df_sub,id.vars=c('home','context_no'))
mybrewercolours <- c('#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#a65628')
#df_sub$context_no <- factor(df_sub)
g <- ggplot(data=df_long,aes(context_no,value,group = home, color=home)) + geom_line() + geom_point(aes(shape=home))
g <- g +  labs(x = "Window size (Hours)", y='Fscore')  + scale_color_brewer(palette = 'Set1') 
g <- g + theme(axis.text = element_text(color="Black",size = 9),legend.text = element_text(size = 7),legend.position = c(0.6,0.22), legend.title = element_blank()) + scale_x_continuous(breaks = c(1,2,3,4,6,8),labels= c(24,12,8,6,4,3))
g <- g + guides(col = guide_legend(nrow = 2 )) 
g

ggsave("context_senstivity.pdf", width = 4, height = 2.5,units = "in")





df_alpha = df[df$context_no == 4 & df$sigma == 2,]
keep <- c('home','alpha','fscore')
df_sub <- df_alpha[keep]
df_long = reshape2::melt(df_sub,id.vars=c('home','alpha'))
g <- ggplot(data=df_long,aes(alpha,value,group = home,color=home)) + geom_line() + geom_point(aes(shape=home))
g <- g +  labs(x = "\u03B1", y='Fscore')  + scale_color_brewer(palette = 'Set1')
g <- g + theme(axis.text = element_text(color="Black",size = 9),legend.text = element_text(size = 7),legend.position = c(0.5,0.18), legend.title = element_blank())
g <- g + guides(col = guide_legend(nrow = 2 )) 
g
ggsave("alpha_senstivity.pdf", width = 4, height = 2.5,units = "in")
#cairo_pdf("alpha_temp.pdf", width = 4, height = 2.5)




df_sigma = df[df$context_no == 4 & df$alpha == 2,]
df_sigma = df_sigma[df_sigma$sigma <=3,]
keep <- c('home','sigma','fscore')
df_sub <- df_sigma[keep]
df_long = reshape2::melt(df_sub,id.vars=c('home','sigma'))
g <- ggplot(data=df_long,aes(sigma,value, group = home, color=home)) + geom_line() + geom_point(aes(shape=home))
g <- g +  labs(x = "n", y='Fscore')  + scale_color_brewer(palette = 'Set1')
g <- g + theme(axis.text = element_text(color="Black",size = 9),legend.text = element_text(size = 7),legend.position = c(0.6,0.18), legend.title = element_blank())
g <- g + guides(col = guide_legend(nrow = 2 )) 
g
ggsave("sigma_senstivity.pdf", width = 4, height = 2.5,units = "in")