# Discord Multi-Spam Bot

basic bot for spamming messages using user tokens and webhooks(needs some fixing)   

## Commands

use `|` to separate commands   
add `-loop` at the end of cmd to loop it   

- dxv3send [channel_id] [cmds]  
- dxv3webhook [channel_id] [webhook_name] [amount]  
- dxv3hookspam [webhook_id] [messages]  
- dxv3spamall [channel_id] [messages]  
- dxv3stop  
- dxv3h

e.g. dxv3send 1257329585213673497 hi | hi again | hi AGAIN!! -loop  

replace `BOT_TOKEN` on line 8    
put tokens in tokens.txt
