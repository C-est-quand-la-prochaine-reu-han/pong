# **************************************************************************** #
#                                                                              #
#                                                               ++             #
#    Makefile                                                  +**+   +*  *    #
#                                                              ##%#*###*+++    #
#    By: aboyreau <bnzlvosnb@mozmail.com>                     +**+ -- ##+      #
#                                                             # *   *. #*      #
#    Created: 2024/09/02 16:08:52 by aboyreau          **+*+  * -_._-   #+     #
#    Updated: 2024/09/02 17:20:12 by aboyreau          +#-.-*  +         *     #
#                                                      *-.. *   ++       #     #
# **************************************************************************** #

all:
	source venv/bin/activate; python pong.py

init:
	python3 -m venv venv || python3 -m virtualenv venv
	source venv/bin/activate ; pip install -r requirements.txt

