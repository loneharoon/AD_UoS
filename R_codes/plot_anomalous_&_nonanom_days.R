
library(reshape2)
library(ggplot2)
library(data.table)
library(fasttime)
library(xts)
Sys.setenv('TZ'='UTC')
setwd('/Volumes/MacintoshHD2/Users/haroonr/Dropbox/Writings/UoS/anom_plots/')

rootdir <- "/Volumes/MacintoshHD2/Users/haroonr/Detailed_datasets/REFITT/REFIT_selected/"
home <- "House20.csv"
df <- fread(paste0(rootdir, home))
# home10(ChestFreezer),  home16(Fridge-Freezer_1),home18(Fridge-Freezer),  home20(Freezer)
df_xts <- xts(df$'Freezer', fastPOSIXct(df$Time))
df_xts_sub <- resample_UTC_data_minutely(df_xts, 1)

date1 <- '2014-05-05' # normal
date2 <-'2014-06-21'  # anomalous
day1 <- df_xts_sub[date1]
day2 <- df_xts_sub[date2]
temp <- data.frame(coredata(day1), coredata(day2))
colnames(temp) <-  c('day1','day2')
temp$timestamp = index(day1)
df_long <- reshape2::melt(temp,id.vars = "timestamp")
g <- ggplot(df_long,aes(timestamp,value ,group = variable,color = variable, size = variable)) + geom_line()
g <- g + scale_color_manual(values=c('blue','black')) + scale_size_manual(values=c(0.4, 0.7))
g <- g + theme(legend.position="none",axis.text=element_text(color="black")) + scale_x_datetime(labels=scales::date_format("%H:%M")) + labs(x= "Hour of the day", y = "Power (W)")
g
savename <- paste0(strsplit(home,'[.]')[[1]][1],'_',date1,'_',date2,".pdf")
ggsave(savename, width = 3 ,height = 2 ,units=c('in'))