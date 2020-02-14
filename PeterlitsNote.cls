\ProvidesClass{PeterlitsNote}
\LoadClass{ctexbook}

\RequirePackage[nosfdefault]{sourcesanspro}
\RequirePackage[shortlabels]{enumitem}
\RequirePackage{amsmath}
\RequirePackage{listings}
\RequirePackage[x11names]{xcolor}
\setlist{leftmargin=2em, itemsep=0.1em, parsep=0em,
    itemindent=0em, listparindent=0em,
    labelwidth=1.5em, labelsep=1em}

\setlength{\marginparwidth}{0pt}
\RequirePackage[top=3.7cm, left=4.2cm, bottom=3.7cm, right=3.2cm, includehead, includefoot]{geometry}

\lstset{
  basicstyle=\fontsize{8.5pt}{10.2pt}\ttfamily\color{Green4!5!black},
  frame=tRBl,
  breakatwhitespace=false,
  keywordstyle=\color{Green4!50!black},
  commentstyle=\color{Gray0!50!black},
  stringstyle=\color{Orange4!50!black},
  breaklines=true,
  xleftmargin=2.5em,
  showstringspaces=false}

\newcommand{\code}[1]
    { \lstinline[basicstyle=\normalsize\ttfamily]`#1` }
\newcommand{\timetx}[1]
    {\noindent\emph{\small #1}\vspace{2em}}
\newcommand{\x}{\textbackslash}

\renewcommand \thesection {\@arabic\c@section}
\renewcommand \section{\@startsection {section}{1}{\z@}%
                                      {4em \@plus .5ex \@minus 2ex}%
                                      {.4ex \@plus.1ex}%
                                      {\normalfont\Large\bfseries}}

\newenvironment{alist}{\begin{enumerate}}{\end{enumerate}}
\newenvironment{aiter}{\begin{itemize}}{\end{itemize}}