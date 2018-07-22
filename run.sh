function start {
	command screenie -j akeshohseka 'irc3 akesho.ini'
	command pgrep -nf akeshohseka > akesho.pid
}

function test {
    command irc3 akesho.ini
}

function connect {
    if [ ! -f akesho.pid ]; then
        echo "Bot is not running."
    else
        command screen -r akeshohseka
   fi
}

function halt {
	if [ -f akesho.pid ]; then
		pkill -F akesho.pid
		rm akesho.pid
	fi
}

if [ $1 == '' ]; then
    echo "./akesho [start,connect,halt,test]"
else
    $1
fi

