#!/bin/sh
#
# Business Layer - the "Controller" of our MVC.
# v1.0
# index.cgi
#
# PLEASE, DO NOT EDIT THESE VARIABLES. If you need to make a change, do so in
# the following config files:
#   - wiki.conf
#   - templates.conf
#
# USEFUL RESOURCES IN THIS DEVELOPMENT: 
# http://paulturner.me/2009/07/reading-http-post-data-using-bash/
# http://www.ffnn.nl/pages/articles/linux/cgi-scripting-tips-for-bash-or-sh.php
#
# TODO: Implement a translating engine to get plain text from the DB and 
#       compile it into pretty markup, markdown-style.
#


#---- Preprocessor variables ----#

title="Nothing"
content="Nothing yet"

command=$(echo "$QUERY_STRING" | cut -d "&" -f 1 | cut -d "=" -f 1)
argument=$(echo "$QUERY_STRING" | cut -d "&" -f 1 | cut -d "=" -f 2)

editable=""

# a show for the home page
home_cont="
<p>
    Welcome to <strong>MyWiki</strong>, the simple wiki. Search for, create
    and edit your pages at will!
</p>
<p>
    If you need help, <a href=\"http://sonokisworld.appspot.com/contact\">
    get in touch with me</a>. I am yet to implement proper documentation here.
    But, most importantly, HAVE FUN!
</p>"

help_cont="
<p>
    <strong>MyWiki</strong> is a ready-to-deploy, out-of-the-box wiki engine
    for Unix servers that requires little to no configuration.
</p>
<p>
    To create a new wiki page, click <strong>Create a new page</strong> in the
    menu. The page editor allows only for plain text (no hyperlinks or other
    formatting) to be used, but paragraphs are separated by inserting two
    consecutive line breaks. Hopefully, future releases of MyWiki will include
    a simple plain text to html interpreter similar to 
    <a href=\"http://daringfireball.net/projects/markdown/\">MarkDown</a> so 
    that the possibilities are expanded, images included.
</p>
<p>
    Note that you can edit any page that you have created (not including these
    predefined ones) by clicking <strong>Edit this page</strong> on the top
    right corner of an existing page.
</p>
"

# boilerplate to create new pages:
# UPDATE: now a function!
# 1 ) The title of the page (empty if new)
# 2 ) The content of the page (empty if new)
# 3 ) The tag <input type="hidden" name="update" value="true" /> (empty if new)
# 4 ) The pid of the page (empty if new)
create_cont() {
    echo "
<form action=\"index.cgi\" method=\"post\">
    <label for=\"newtitle\">Page title:</label><br />
    <input type=\"text\" name=\"newtitle\" value=\""$1"\" /><br />
    <label for=\"newcontent\">Page content:</label><br />
    <textarea name=\"newcontent\" rows=\"80\" cols=\"40\">"$2"</textarea><br />
    <input type=\"submit\" value=\"Create page\" />
    $3<input type=\"hidden\" name=\"pid\" value=\"$4\" />
</form>"
}

# Routine to report errors:
show_error() {
    # pass an explanation of the error as the first argument.
    echo "Status: 500"
    echo "Content-Type: text/html"
    echo ""
    echo "<h1>500 - INTERNALSERVER ERROR</h1>"
    echo "<p>The innards of the system suffered an error.
          Don't worry, though, it wasn't your fault.</p>"
    echo "<p>The most probable cause of the error is this: $1</p>"
    echo "<p>Please try again. If this problem persists, get in touch 
          with the administrator.</p>"
    exit
}


# URL string decoder:

unescape() {
    # take an input string as the only argument to store it in the base.
    # HINT: the newlines appear like this:
    # %0D%0A %0D%0A
    # These, for the sake of our CMS-ish wiki system, will need to be converted
    # into <p> tags, that is, at FETCH time, not storage time!
    # TODO: allow for some Unicode characters?

    echo "$1" | sed s/^/\<p\>/ | 
    sed s#$\#\</p\>#g | 
    sed s/%22/"\&quot\;"/g | 
    sed s/%21/\!/g |
    sed s/%2C/,/g |
    sed s/%27/"\&#39\;"/g |
    sed s/%28/\(/g |
    sed s/%3F/\?/g |
    sed s/%29/\)/g |
    tr "+" " " |
    sed s/%3C/"\&lt\;"/g |
    sed s/%3E/"\&gt\;"/g |
    sed s@%2F@/@g |
    sed s@%0D%0A%0D%0A@\</p\>\<p\>@g 
}


# A proper searching mechanism

search() {
    # arguments: [search string]
    final="<ul>\n"
    ids=$(sqlite3 index.db "SELECT id FROM main WHERE content LIKE '%$1%'")
    if [ -z "$ids" ]; then
        final=$final"Sorry, no results found."
    else
        for result in $ids
        do
            result_t=$(sqlite3 index.db "SELECT title FROM main WHERE id=$result")
            final=$final"<li><a href=\"index.cgi?p=$result\">""$result_t""</a></li>\n"
        done
    fi
    final="$final</ul>"
    echo -e "$final"
}

# Debug for post string format; pass the postdata as the first argument.

post_debug() {
    echo "Content-Type: text/html; charset=utf-8"
    echo ""
    echo "<h1>Diagnostics for POST string</h1>
    <p>You entered the following query string as POST:</p>
    <p>
        <pre>$1</pre>
    </p>
    <p>
        Diagnostics end here.
    </p>"
    exit
}


#---- Logical flow ----#

if [ "$REQUEST_METHOD" == "GET" ]; then
    # Either serve a page or search for one.
    case "$command" in
        "p" )
            title=$(sqlite3 index.db "SELECT title FROM main WHERE id=$argument")
            content=$(sqlite3 index.db "SELECT content FROM main WHERE id=$argument")
            editable="<a style=\"float: right\" href=\"index.cgi?edit=$argument\">Edit this page</a>"
            ;;
        "search" ) 
            argument=$(echo "$argument" | tr "+" " ")
            title="Search results for \"$argument\""
            content=$(search "$argument")
            ;;
        "create" )
            title="Create a new page:"
            content=$(create_cont)
            ;;
        "all" ) 
            title="All pages in this wiki"
            content=$(search)
            ;;
        "about" ) 
            title="About MyWiki"
            content="$help_cont"
            ;;
        "edit" )
            title="Now editing \"$(sqlite3 index.db "SELECT title FROM main WHERE id=$argument")\""
            content=$(create_cont "$(sqlite3 index.db "SELECT title FROM main WHERE id=$argument")" "$(sqlite3 index.db "SELECT content FROM main WHERE id=$argument")" "<input type=\"hidden\" name=\"update\" value=\"true\" />" $argument)
            ;;
        * ) # Serve the home page.
            title="MyWiki Home"
            content="$home_cont"
            ;;
    esac

else if [ "$REQUEST_METHOD" == "POST" ]; then 
    # NOTE: the query string for post goes like this:
    # newtitle=this+is+an+example+title&newcontent=Here+goes+some+content
    if [ "$CONTENT_LENGTH" -gt 0 ]; then
        read -n $CONTENT_LENGTH postdata <& 0
    fi
    title=$(echo $postdata | cut -d "&" -f 1 | cut -d "=" -f 2 | tr "+" " ")
    content=$(echo $postdata | cut -d "&" -f 2 | cut -d "=" -f 2)
    editing=$(echo $postdata | cut -d "&" -f 3 | cut -d "=" -f 2)
    argument=$(echo $postdata | cut -d "&" -f 4 | cut -d "=" -f 2)
    content=$(unescape "$content")
    #post_debug "$argument"

    # Hey, the folder that contains 'index.db' must also be owned by the www
    # user, otherwise a clash of permissions ensues!
    if [ "$editing" == "true" ]; then
        sqlite3 index.db "UPDATE main SET title = \"$title\", content = \"$content\" WHERE id=$argument" || show_error "$argument"
    else
        sqlite3 index.db "INSERT INTO main (title, content) VALUES ('$title', \"$content\")" ||
            show_error "permission error"
    fi

    # Load the brand-new page!
    argument=$(sqlite3 index.db "SELECT id FROM main WHERE title = '$title'")
    title=$(sqlite3 index.db "SELECT title FROM main WHERE id=$argument")
    content=$(sqlite3 index.db "SELECT content FROM main WHERE id=$argument")
    editable="<a style=\"float: right\" href=\"index.cgi?edit=$argument\">Edit this page</a>"
fi
fi


#---- Set the HTTP Headers ----#

echo "Status: 200 OK"
echo "Content-Language: en"
echo "Content-Type: text/html; charset=UTF-8"
echo ""


#---- Serve the content ----#

cat <<EOF
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
    <head>
        <title>$title - MyWiki</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
        <link rel="stylesheet" type="text/css" href="style.css" />
    </head>
    <body>
        <header>
            <h1>MyWiki - the simple wiki</h1>
            <nav>
                <div class="menutrigger">Menu</div>
                <ul>
                    <li><a href="index.cgi">Home</a></li>
                    <li><a href="index.cgi?all">All pages</a></li>
                    <li><a href="index.cgi?about=about">About</a></li>
                    <li><a href="index.cgi?about=help">Help</a></li>
                    <li><a href="index.cgi?create=new">Create a new page</a></li>
                    <li><a href="javascript:void(0)" class="search" >Search</a></li>
                    <li class="search">
                        <form action="index.cgi" method="GET">
                            <input type="text" name="search" placeholder="search MyWiki" />
                            <input type="submit" value="search" />
                        </form>
                    </li>
                </ul>
            </nav>
        </header>
        <section id="content">
            $editable
            <h2>$title</h2>
            $content
        </section>
        <footer>
            <p>
                Made with <a href="http://mysimplewiki.googlecode.com">MyWiki, the Simple Wiki</a> - Est. 2014
            </p>
        </footer>
        <script type="text/javascript" src="main.js"></script>
    </body>
</html>
EOF

