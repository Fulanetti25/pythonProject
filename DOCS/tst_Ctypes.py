# Styles:
# 0 : OK
# 1 : OK | Cancel
# 2 : Abort | Retry | Ignore
# 3 : Yes | No | Cancel
# 4 : Yes | No
# 5 : Retry | Cancel
# 6 : Cancel | Try Again | Continue

import ctypes

msg = 'Olá mundo'
title = 'teste'
style = 5
ctypes.windll.user32.MessageBoxW(0,title,msg,style)
