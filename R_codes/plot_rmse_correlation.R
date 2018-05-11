# use this script to plot rmse and corelation for UK work
library(ggplot2)
library(xts)
library(fasttime)
library(reshape2)
setwd('/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/Intermediary_results/paper_plots/')

 # RMSE
columnhead <- c('Home1', 'Home10', 'Home16', 'Home18', 'Home20')
CO <- c(286, 47,	65,	113,	117)
FHMM <- c(336,45,	66,	69,	129)
LBM <- c(425,	60,	58,	80,	77)
SSHMM <- c(240,	51,	66,	70,	60)
GSP <- c(355,	54,	89,	164, 70)

resdata = as.data.frame(rbind(CO,FHMM, LBM, SSHMM, GSP))
colnames(resdata) <-  columnhead
resdata['Approach'] <- rownames(resdata)

df_melt=  reshape2::melt(resdata,id.vars= c('Approach'))
mybrewercolours <- c('#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#a65628')
h <- ggplot(df_melt,aes(variable,value))  + geom_bar(aes(fill= Approach),position="dodge",stat="identity",width = 0.4 )
h <- h +  labs(x = "", y='RMSE (Lower is better)', fill="Approach")  + scale_fill_manual(values = mybrewercolours)
h <- h + theme(axis.text = element_text(color="Black",size = 9),legend.text = element_text(size = 7)) 
h <- h + theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
               panel.background = element_blank(), axis.line = element_line(colour = "grey"))
h <- h + theme(legend.position = c(0.8,0.7), legend.text = element_text(color="Black",size = 9)) 
h
#ggsave("rmse.pdf", width = 6, height = 3,units = "in") 

# CORRELATION 
columnhead <- c('Home1', 'Home10', 'Home16', 'Home18', 'Home20')

CO <- c(0.66,	0.03,0.01,	0.17,	0.25)
FHMM <- c(	0.54,	0.08,	0.02,	0.25,	0.25)
LBM <- c(0.27,	0.08,	0.01,	0.07,	0.26)
SSHMM <- c(0.67,	0.08,	0.04,	0.32,	0.46)
GSP <- c(0.22,	0.17,	0.01,	0.02,	0.32)

resdata = as.data.frame(rbind(CO,FHMM, LBM, SSHMM, GSP))
colnames(resdata) <-  columnhead
resdata['Approach'] <- rownames(resdata)
df_melt=  reshape2::melt(resdata,id.vars= c('Approach'))
mybrewercolours <- c('#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#a65628')
h <- ggplot(df_melt,aes(variable,value))  + geom_bar(aes(fill= Approach),position="dodge",stat="identity",width = 0.4 )  
#+ guides(col = guide_legend(nrow = 2, byrow= TRUE)) 
h <- h +  labs(x = "", y='Correlation  Coefficient', fill="Approach")  + scale_fill_manual(values = mybrewercolours)
h <- h + theme(axis.text = element_text(color="Black",size = 9))  
theme(legend.)
h <- h + theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
               panel.background = element_blank(), axis.line = element_line(colour = "grey")) 
h <- h + theme(legend.position = 'top', legend.text = element_text(color="Black",size = 9)) 
h
ggsave("correlation_plot.pdf", width = 6, height = 3,units = "in") 
