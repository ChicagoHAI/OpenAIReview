% !TEX encoding = UTF-8 Unicode
\documentclass[pdflatex]{sn-jnl}% 
\newcommand*\tcircle[1]{%
  \raisebox{-0.5pt}{%
    \textcircled{\fontsize{7pt}{0}\fontfamily{phv}\selectfont #1}%
  }%
}\usepackage{amssymb}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{graphicx}%
\usepackage{multirow}%
\usepackage{amsmath,amssymb,amsfonts}%
\usepackage{amsthm}%
\usepackage{mathrsfs}%
\usepackage[title]{appendix}%
\usepackage{xcolor}%
\usepackage{textcomp}%
\usepackage{manyfoot}%
\usepackage{booktabs}%
\usepackage{algorithm}%
\usepackage{algorithmicx}%
\usepackage{algpseudocode}%
\usepackage{listings}%
%%%%

%%%%%=============================================================================%%%%
%%%%  Remarks: This template is provided to aid authors with the preparation
%%%%  of original research articles intended for submission to journals published 
%%%%  by Springer Nature. The guidance has been prepared in partnership with 
%%%%  production teams to conform to Springer Nature technical requirements. 
%%%%  Editorial and presentation requirements differ among journal portfolios and 
%%%%  research disciplines. You may find sections in this template are irrelevant 
%%%%  to your work and are empowered to omit any such section if allowed by the 
%%%%  journal you intend to submit to. The submission guidelines and policies 
%%%%  of the journal take precedence. A detailed User Manual is available in the 
%%%%  template package for technical guidance.
%%%%%=============================================================================%%%%

%% as per the requirement new theorem styles can be included as shown below
\theoremstyle{thmstyleone}%
\newtheorem{theorem}{Theorem}%  meant for continuous numbers
%%\newtheorem{theorem}{Theorem}[section]% meant for sectionwise numbers
%% optional argument [theorem] produces theorem numbering sequence instead of independent numbers for Proposition
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\newtheorem{proposition}[theorem]{Proposition}% 
%%\newtheorem{proposition}{Proposition}% to get separate numbers for theorem and proposition etc.

\theoremstyle{thmstyletwo}%
\newtheorem{example}{Example}%
\newtheorem{remark}{Remark}%

\theoremstyle{thmstylethree}%
\newtheorem{definition}{Definition}%

\raggedbottom
%%\unnumbered% uncomment this for unnumbered level heads

\DeclareMathOperator{\loc}{loc}
\DeclareRobustCommand\full  {\tikz[baseline=-0.6ex]\draw[thick] (0,0)--(0.5,0);}
\DeclareRobustCommand\dotted{\tikz[baseline=-0.6ex]\draw[thick,dotted] (0,0)--(0.54,0);}
\DeclareRobustCommand\dashed{\tikz[baseline=-0.6ex]\draw[thick,dashed] (0,0)--(0.54,0);}
\DeclareRobustCommand\chain {\tikz[baseline=-0.6ex]\draw[thick,dash dot dot] (0,0)--(0.5,0);}
\DeclareRobustCommand\oline{%
\tikz[baseline=-0.6ex]{
  \draw[thick] (0,0)--(0.5,0);
  \filldraw (0.25,0) circle (1.5pt);
}}
\DeclareRobustCommand\chainn{\tikz[baseline=-0.6ex]\draw[thick,dash dot] (0,0)--(0.5,0);}
% \usepackage{tikz}
\usepackage{bbm}
\usepackage[utf8]{inputenc}  
% \usepackage{amsrefs}
\usepackage{amssymb,amsmath}
\usepackage{enumerate}
\usepackage[shortlabels]{enumitem}
\usepackage{mathtools}
\usepackage{graphicx}
%\usepackage{upref}
\usepackage{url}
%\usepackage{hyperref}
%\usepackage[pdftex, colorlinks=true, backref]{hyperref}
\usepackage{color}  
\definecolor{darkred}{rgb}{0.6,0,0}
\definecolor{darkgreen}{rgb}{0,0.5,0}
\definecolor{darkmagenta}{rgb}{0.5,0,0.5}
% \usepackage[pdftex, colorlinks=true,
%   linkcolor=darkred,
%   citecolor=darkgreen,
%   urlcolor=darkmagenta]{hyperref}
  
% \usepackage[notref,notcite]{showkeys}
\usepackage[capitalize,nameinlink]{cleveref}
%\usepackage{refcheck}

\makeatletter
\def\@cite#1#2{\textup{[{#1\if@tempswa , #2\fi}]}}
\makeatother

%--------- from mathtools
\DeclarePairedDelimiter\abs{\lvert}{\rvert}
\DeclarePairedDelimiter\norm{\lVert}{\rVert}
%  use \abs*{x} to get scaled delimiters
%  use \abs[\Bigg]{x} to get fixed delimiters
%
% construction of sets
% just to make sure it exists
   \providecommand\given{}
   % can be useful to refer to this outside \Set
   \newcommand\SetSymbol[1][]{%
      \nonscript\:#1\vert
      \allowbreak
      \nonscript\:
      \mathopen{}}
   \DeclarePairedDelimiterX\Set[1]\{\}{%
      \renewcommand\given{\SetSymbol[\delimsize]}
      #1
   }
%------- end of construction of sets  

%\newcommand{\abs}[1]{\left\vert#1\right\vert}
%\newcommand{\norm}[1]{\left\Vert#1\right\Vert}

%  use \abs*{x} to get scaled delimiters
%  use \abs[\Bigg]{x} to get fixed delimiters
%
% construction of sets
% just to make sure it exists
   \providecommand\given{}
   % can be useful to refer to this outside \Set

\newcommand{\R}{\mathbb R}
\newcommand{\N}{\mathbb N}
\newcommand{\calH}{\mathcal H}
\newcommand{\Oh}{\mathcal O}
\newcommand{\oh}{\mathrm o}
\newcommand{\Dt}{{\Delta t}}
\newcommand{\dd}[1]{\mathrm{d}#1}
\newcommand{\dott}{\, \cdot\,}
\newcommand{\marginlabel}[1]{\mbox{}\marginpar{\raggedleft\hspace{0pt}\tiny#1}}
\newcommand{\arxiv}[1]{\href{https://arxiv.org/pdf/#1}{arXiv:#1}} 
\newcommand{\indic}[1]{\mathbf{1}_{\{#1\}}}
\newcommand{\iverson}[1]{[#1]}

%By Us%
%\usepackage{amsrefs}
 \usepackage[sort]{cite}
\usepackage{bigints}
\newcommand{\Z}{\mathbb{Z}}
\DeclareMathOperator{\lip}{Lip}
\DeclareMathOperator{\bv}{BV}
\newcommand{\sgn}{\mathop\mathrm{sgn}}
\newcommand{\norma}[1]{{\left\|#1\right\|}}
\newcommand{\normal}[1]{{\left|#1\right|}}
\renewcommand{\d}[1]{\mathinner{\mathrm{d}{#1}}}
%\newcommand{\BV}{BV}
\DeclareMathOperator{\TV}{TV}
\DeclareMathOperator{\lipR}{Lip(\R)}
\newcommand{\D}{\Delta}
\newcommand{\modulo}[1]{{\left|#1\right|}}
\renewcommand{\L}[1]{\mathbf{L^#1}}
% \newcommand{\Lloc}[1]{\mathbf{L^{#1}_{loc}}}


\numberwithin{equation}{section}     
\allowdisplaybreaks

\begin{document}
\title[]{Systems of Nonlocal Conservation Laws with Memory and Their Zero Retention Limit}
\author*[1]{\fnm{Aekta} \sur{Aggarwal}}\email{aektaaggarwal@iimidr.ac.in}

\author[2]{\fnm{Ganesh} \sur{Vaidya}}\email{vaidyaganesh@iisc.ac.in}

\affil*[1]{\orgdiv{Operations Management and Quantitative Techniques}, 
\orgname{Indian Institute of Management Indore}, 
\orgaddress{\street{Prabandh Shikhar, Rau--Pithampur Road}, 
\city{Indore}, \postcode{453556}, \state{Madhya Pradesh}, \country{India}}}

\affil[2]{\orgdiv{Department of Mathematics}, 
\orgname{Indian Institute of Science}, 
\orgaddress{\city{Bangalore}, \postcode{560012},  \state{Karnataka}, \country{India}}}
\date{\today} 



%\dedicatory{}


% \begin{document}
 \abstract{
We study the entropy solution for a class of systems of nonlocal conservation laws in which the convective flux is convoluted with a kernel in both spatial and temporal variables. This formulation models the flux dependence on the solution within its spatial neighborhood (nonlocal in space) as well as on prior states in time (nonlocal in time), thereby incorporating memory effects. In addition, employing a convergent finite volume approximation, the existence of the entropy solution is discussed. The uniqueness
of such entropy solutions is also established.

In addition, we analyze the asymptotic behavior of the solutions as the
support of the temporal convolution kernel shrinks, demonstrating the “memory-
to-memoryless” effect and convergence to the entropy solution of the corresponding nonlocal conservation law without memory (i.e., nonlocal only in
space). Convergence rate estimates are derived. In addition, the proposed numerical approximations are shown to be asymptotically compatible with this
passage to the memoryless limit by deriving the corresponding asymptotic
convergence rate estimates. The analysis is carried out in a very general set-
ting, without imposing any geometric restrictions such as the convexity of the
spatial and temporal convolution kernels, unlike the existing literature on the
asymptotic analysis of nonlocal-in-space only conservation laws. To the best
of our knowledge, this provides the first convergence and asymptotic analysis
for finite volume schemes applied to nonlocal conservation laws with memory. Numerical experiments are included to illustrate the theory.
}
% \begin{abstract}
%     In this work, we investigate entropy solutions for a class of systems of nonlocal conservation laws in which the convective flux is convolved with a kernel in both spatial and temporal variables. This formulation models the flux dependence on the solution within its spatial neighborhood (nonlocality in space) as well as on prior states in time (nonlocality in time), thereby incorporating memory effects. The systems are strongly coupled through the nonlocal terms. We discuss the convergence of the finite volume approximations, thereby establishing the existence of entropy solutions. {\color{red}The uniqueness of such entropy solutions is also established.}

% In addition, we analyze the asymptotic behavior of the solutions as the support of the temporal convolution kernel shrinks, demonstrating the {“memory-to-memoryless”} effect and convergence to the entropy solution of the corresponding nonlocal conservation law without memory (i.e., nonlocal only in space). Convergence rate estimates are derived. In addition, the proposed numerical approximations are shown to be asymptotically compatible with this passage to the memoryless limit by deriving the corresponding asymptotic convergence rate estimates. The analysis is carried out in a very general setting, without imposing any geometric restrictions such as the convexity of the spatial and temporal convolution kernels, unlike the existing literature on the asymptotic analysis of nonlocal-in-space only conservation laws. 
% To the best of our knowledge, this provides the first convergence and asymptotic analysis
% for finite volume schemes applied to nonlocal conservation
% laws with memory.


% % To the best of our knowledge, this is the first convergence analysis of nonlocal conservation laws with memory.
% % \end{abstract}
% \begin{abstract}
% {Check one, tighetend it}
% We study entropy solutions for a class of systems of nonlocal conservation laws in which the convective flux is convolved with kernels in both space and time. This formulation models spatial nonlocal interactions and temporal memory effects, and induces strong coupling through the nonlocal terms. We prove convergence of finite volume approximations and thereby establish existence and uniqueness of entropy solutions.

% We further analyze the asymptotic regime in which the support of the temporal kernel vanishes, showing convergence to the entropy solution of the corresponding memoryless (purely spatially nonlocal) system. Quantitative convergence rates are derived. Moreover, we prove that the proposed numerical scheme is asymptotically compatible with this limit by establishing matching asymptotic convergence rates.

% Our analysis is carried out in a general framework without imposing geometric conditions such as convexity of the spatial or temporal kernels, in contrast to existing results for nonlocal-in-space conservation laws. To the best of our knowledge, this is the first work to provide both convergence and asymptotic analysis for finite volume schemes applied to nonlocal conservation laws with memory.
% \end{abstract}
% \maketitle

% \begin{keywords}
%   nonlocal conservation laws, traffic model with memory, memory-to-memoryless, finite volume schemes, error estimate,  and asymptotic compatibility
% \end{keywords}

% % REQUIRED
% \begin{AMS}
% 65M08, 65M15, 35L65, 65M25, 35D30, 65M12 
%   %68Q25, 68R10, 68U05
% \end{AMS}
%  \begin{abstract}
% In this work, we investigate the entropy solution for a class of systems of nonlocal conservation laws in which the convective flux is convoluted with a kernel in both spatial and temporal variables. This formulation models the flux dependence on the solution within its spatial neighborhood (nonlocality in space) as well as on prior states in time (nonlocality in time), thereby incorporating memory effects. In addition, employing a convergent finite volume approximation, the existence of the entropy solution is established.  Additionally, the asymptotic behavior of the solution as the temporal convolution kernel’s support shrinks, is analyzed, demonstrating the fading memory effect of the system and the asymptotic convergence to the entropy solution of the corresponding nonlocal conservation law without memory (i.e., nonlocal only in space). In addition,  the proposed numerical approximations are shown to to be asymptotically compatible with this passage of the limits ( ``memoryless" limits)  by deriving the asymptotic convergence rate estimates.
% % Finally, we derive explicit rates for this convergence with respect to the memory parameter. 
% % Numerical experiments illustrating the theory are presented. 
% The analysis has been done in a very general setup without imposing any restrictions on the geometry such as convexity of both space and time convolutions kernels, unlike the exiting literature on asymptotic analysis. To the best of our knowledge, this is the first convergence analysis of nonlocal conservation laws with memory.
% {\color{black}The analysis is carried out in a very general setting, without imposing any geometric restrictions such as the convexity of the spatial and temporal convolution kernels, unlike the existing literature on asymptotic analysis.}
% \end{abstract}
% \begin{abstract}
%     In this work, we investigate entropy solutions for a class of systems of nonlocal conservation laws in which the convective flux is convolved with a kernel in both spatial and temporal variables. This formulation models the flux dependence on the solution within its spatial neighborhood (nonlocality in space) as well as on prior states in time (nonlocality in time), thereby incorporating memory effects. The systems are strongly coupled through the nonlocal terms. We discuss the convergence of the finite volume approximations, thereby establishing the existence of entropy solutions. {\color{red}The uniqueness of such entropy solutions is also established.}

% In addition, we analyze the asymptotic behavior of the solutions as the support of the temporal convolution kernel shrinks, demonstrating the {“memory-to-memoryless”} effect and convergence to the entropy solution of the corresponding nonlocal conservation law without memory (i.e., nonlocal only in space). Convergence rate estimates are derived. In addition, the proposed numerical approximations are shown to be asymptotically compatible with this passage to the memoryless limit by deriving the corresponding asymptotic convergence rate estimates. The analysis is carried out in a very general setting, without imposing any geometric restrictions such as the convexity of the spatial and temporal convolution kernels, unlike the existing literature on the asymptotic analysis of nonlocal-in-space only conservation laws. 
% To the best of our knowledge, this provides the first convergence and asymptotic analysis
% for finite volume schemes applied to nonlocal conservation
% laws with memory.


% % To the best of our knowledge, this is the first convergence analysis of nonlocal conservation laws with memory.
% \end{abstract}
% \begin{abstract}
% We study entropy solutions for a class of systems of nonlocal conservation laws in which the convective flux is convolved with kernels in both space and time. This formulation models spatial nonlocal interactions and temporal memory effects, and induces strong coupling through the nonlocal terms. We prove convergence of finite volume approximations and thereby establish existence and uniqueness of entropy solutions.

% We further analyze the asymptotic regime in which the support of the temporal kernel vanishes, showing convergence to the entropy solution of the corresponding memoryless (purely spatially nonlocal) system. Quantitative convergence rates are derived. Moreover, we prove that the proposed numerical scheme is asymptotically compatible with this limit by establishing matching asymptotic convergence rates.

% Our analysis is carried out in a general framework without imposing geometric conditions such as convexity of the spatial or temporal kernels, in contrast to existing results for nonlocal-in-space conservation laws. To the best of our knowledge, this is the first work to provide both convergence and asymptotic analysis for finite volume schemes applied to nonlocal conservation laws with memory.
% \end{abstract}

\pacs[MSC Classification]{35L65,65M25, 35D30,  65M12, 65M15}

\keywords{nonlocal conservation laws, traffic flow,convergence rate, hyperbolic systems, adapted entropy}


\maketitle

% \begin{keywords}
%   nonlocal conservation laws, traffic model with memory, memory-to-memoryless, finite volume schemes, error estimate,  and asymptotic compatibility
% \end{keywords}

% % REQUIRED
% \begin{AMS}
% 65M08, 65M15, 35L65, 65M25, 35D30, 65M12 
%   %68Q25, 68R10, 68U05
% \end{AMS}

\section{Introduction}
Many real-world phenomena exhibit dynamics in which the state at a given time depends not only on the present configuration but also on the past history of the system. In such settings, the notion of “memory” 
captures the influence of previous states on the current dynamics. Such hereditary structures appear in industrial applications such as damping phenomena in elastic media~\cite{CHR2007,c2008}, viscoelasticity~\cite{Dafermos1970}, models involving fractional-in-time behavior \cite{Podlubny1999},  gas transport models in coal seams involving adsorption and diffusion in meso and micropores~\cite{Clarkson1999,Shi2003}, and transport models in subsurface and hyporheic zones~\cite{Haggerty1995,Gooseff2003,Haggerty2002}. A prototypical scalar conservation law modeling such events,  reads as follows:
\begin{equation}\label{eq:memory_general}
\partial_t u
- \partial_x \Big( \, f(u,\int_0^t u(\tau,x)\Gamma(t-\tau))\, d\tau \Big)
=0, \quad (t,x) \in Q_T:= (0,T)\times\R,
\end{equation}
where $\Gamma$ is a temporal memory kernel.
Despite their applications in modeling a wide range of phenomena, the well-posedness theory for such models remains largely incomplete. One key difficulty is that the temporal convolution term often lacks spatial smoothness, rendering the flux discontinuous as a function of the spatial variable. The presence of temporal convolution destroys the semigroup property in the usual sense and gives rise to a new mathematical object, unlike those arising in local or purely spatially nonlocal conservation laws. %{\color{red}}
%introduces substantial analytical challenges in the study of stability and compactness. 
Consequently, classical methods for standard conservation laws do not directly apply. Some studies ~\cite{c2008,N2023, DHSS2023, P2014,liu2020, Dafermos1970, D1987, CC2007,DAF2012,CHR2007} deal with some specific cases  exploiting structural properties of particular PDEs to study the wellposedness, under some specialized assumptions on the flux. 
% and subsequently, fading memory effects—where the convolution kernel shrinks in time radius  characterizing limiting behavior. However, these approaches often require specialized assumptions on the flux. 

However, the case of ``nonlocal space only" conservation laws, \begin{align}
% \begin{split}
    \label{nls1}
  \partial_t u +\partial_x \Big(f(u,\int_{\R} u(t,\xi)\mu(x-\xi))\, d\xi \Big)&=0, \quad (t,x) \in Q_T,
  % \\
  % \label{init}
  % U^{k}(0,x)&=U_0^{k}(x), \quad x \in \R,
%   \end{split}
% \end{align} ,
% \,\quad (t,x) \in Q_T:= (0,T)\times\R, \\ 
% % \label{eq:umuli}
%  \boldsymbol{U}(0,x)&=\boldsymbol{U}_0(x), \quad x \in\R,
 % \end{split}
% \label{sc}
 % \begin{split}
% \partial_t U^{k} +\partial_x \Big(f^k(U^k) \nu^k((\boldsymbol{\mu} \circledast  \boldsymbol{U})^k)\Big) &=0, \quad (t,x) \in Q_T,k\in\mathcal{N}\\
% (\mu^{j,k}*U^j)(t,x)&:=\displaystyle\int_{\R} U^j(t,\xi)\mu^{j,k}(x-\xi)  \d \xi,
% \end{split}
\end{align} with $\mu$ being a spatial horizon kernel, has gained significant interest in the recent decade,  due to two reasons: their widespread use in  modeling of applications where the flux at a given point may depend 
not only on the local state but also on averaged quantities over a finite 
interaction horizon, for example,  crowds \cite{CGL2012,ACG2015}, traffic \cite {BG2016,BHL2023,FGKP2022,AHV2023_1,AHV2024}, sedimentation
models \cite{BBKT2011}, {laser technology \cite{CM2015}},  granular material dynamics \cite{AS2012}, conveyor belt dynamics \cite{GHS+2014},  opinion formation~\cite{ANT2007}, sedimentation
models~\cite{BBKT2011} and  granular material dynamics~\cite{AS2012} etc, and their analytical/mathematical vicinity to local nonlinear conservation laws. Its well-posedness has been well studied in literature, a non-exhaustive list being \cite{CK24,FGR2021,BFK2022,AV2023,FCV2023,KP2021,CG2019, KLS2018,ANT2007,AS2012,BHL2023, ACT2015, AG2016,BG2016,FGKP2022,CGL2012,AHV2023_1,AHV2024,AHV2023, ACG2015,BBKT2011,GHS+2014,CG2023,CM2015} etc. 
% {\color{black}.}

In contrast, the present article combines these two frameworks by considering convolution kernels that depend on both spatial and temporal variables. 
In particular, we study the initial-value problem (IVP) for the coupled system of $N$ nonlocal hyperbolic conservation laws of the above type, where for every $k\in \mathcal{N}:=\{1, \ldots, N\}$,  the $k^{\rm th}$ equation is given by
% \begin{align}
% \begin{split}
% \label{eq:umulA}
\begin{align}
% \begin{split}
    \label{nlm}
  \partial_t U^{k} +\partial_x \Big(f^k(U^k) \nu^k((\boldsymbol{\Theta} \circledast  \boldsymbol{U})^k)\Big) &=0, \quad (t,x) \in Q_T,\\
  \label{init}
  U^{k}(0,x)&=U_0^{k}(x), \quad x \in \R.
%   \end{split}
% \end{align} ,
% \,\quad (t,x) \in Q_T:= (0,T)\times\R, \\ 
% % \label{eq:umuli}
%  \boldsymbol{U}(0,x)&=\boldsymbol{U}_0(x), \quad x \in\R,
 % \end{split}
 \end{align} Here, $T$ is the final time and the unknown is $\boldsymbol{U}=(U^{k})_{k\in\mathcal{N}}:[0,\infty)\times\mathbb{R}\to\mathbb{R}^N.$ 
Further, for every $j,k\in \mathcal{N}$, ${U}^k_0\in (L^1 \cap \bv) (\R;[0,1]), \Theta^{j,k}(t,x):=\mu^{j,k}(x) \Gamma^{j,k}(t)$, with $\boldsymbol{\mu}$ and $\boldsymbol{\Gamma}$ being smooth $N\times N$ matrices, and $(\boldsymbol{\Theta}\circledast \boldsymbol{U})^k:= (\Theta^{k,i}*U^i)_{i\in\mathcal{N}},$ where for every $(t,x)\in \overline{Q}_T$, \begin{align}\label{mc}
\begin{split}
   (\Theta^{i,k}*U^i)(t,x)&:=\displaystyle\int_0^t\int_{\R} U^i(\tau,\xi)\mu^{j,k}(x-\xi)\Gamma^{i,k}(t-\tau) \d \tau \d \xi, i\in\mathcal{N}.
     % \\  &=\displaystyle\int_0^t\int_{\R}U^k(\tau,x-\xi)\mu^{j,k}(\xi)\Gamma^{j,k}(t-\tau) \d \tau \d \xi.
\end{split}
\end{align} Additionally,
\begin{enumerate}[(\textbf{H\arabic*})]
\item \label{H1A}$f^k \in  \lip(\R)$  with $ f^k(0)=0=f^k(1/2)$.
% be the norm on the product space. 
 \item \label{H2A}$\nu^k \in (C^2 \cap \bv \cap \, W^{2,\infty}) (\R^N,\R)$;
 \item \label{H3A}
 $\Theta^{j,k}(t,x):=\mu^{j,k}(x) / \Gamma^{j,k}(t)$, with $\boldsymbol{\mu}$ and $\boldsymbol{\Gamma}$ being smooth $N\times N$ matrices. The space kernel ${\mu}^{j,k} \in C^2(\R) \cap W^{2,\infty}(\R)$. The time kernel $\Gamma^{j,k}\in C^2([0,\infty);\R^+) \cap W^{2,\infty}([0,\infty);\R^+).$ 
 % and is a non-increasing function.{\color{black}(Comment on physical implication of non-decreasing.)} 
 \end{enumerate} Modeling-wise, it is to be noted that the system \eqref{nlm}--\eqref{init} is coupled through the nonlocal operator
$
\boldsymbol{\Theta}\circledast\boldsymbol{U}$,
which introduces both \emph{spatial averaging} and \emph{temporal memory effects} into the convective flux of \eqref{nlm}.
More precisely, for every $k\in\mathcal{N}$, the flux at a spacetime point $(t_0,x_0)$
depends not only on the instantaneous density $U^k(t_0,x_0)$, but also on
\begin{enumerate}[(i)]
\item a weighted average of the states $U^j(t_0,\cdot)$ in a neighborhood of $x_0$,
determined by the spatial kernel $\mu^{j,k},j,k,\in\mathcal{N}$;
\item a cumulative influence of past states $U^j(\tau,x_0)$, $\tau<t_0$,
modulated by the time kernel $\Gamma^{j,k},j,k,\in\mathcal{N}$.
\end{enumerate}
Consequently, the characteristic speed of the $k^{\mathrm{th}}$ equation at $(t_0,x_0)$
reflects a history-dependent interaction between all components of the system,
rather than being determined solely by local instantaneous data. In practical applications,  $\Gamma^{j,k}$ is typically taken as a decreasing function of time, depicting fading memory and assigning smaller weights to older information. However, the results of this article remain valid for a broader class of $\Gamma^{j,k}$ satisfying \ref{H3A}.
 
 We will show that although a general well-posedness theory for time-nonlocal conservation laws remains largely undeveloped, the present framework enables us to systematically adapt techniques from the theory of purely spatial nonlocal conservation laws to establish well-posedness for a substantially broader class of flux functions incorporating both spatial and temporal nonlocal effects, invoking the  regularity of the convective flux with respect to the space variable $x$.
{
Using relaxation schemes, \eqref{nlm}-\eqref{init} has been recently studied for $N=1$ in \cite{DHSS2023} for a specific choice of $\Theta$ and linear $f$}.
That said, the question of existence as well as uniqueness of the entropy solutions for the system  \eqref{nlm}-\eqref{init} with a general $\boldsymbol{\Theta}$ having temporal dependence and(or) for $N>1$, remains unexplored and unsettled as of now, which is dealt with in the first part of this article. {\color{black}Several further interesting questions} regarding the entropy solution of \eqref{nlm}-\eqref{init} are: 
\begin{enumerate}[(\textbf{Q\arabic*})]
\item \label{a} Does it converge to the entropy solution of its ``nonlocal-space'' counterpart \begin{align}
% \begin{split}
    \label{nls}
  \partial_t U^{k} +\partial_x \Big(f^k(U^k) \nu^k((\boldsymbol{\mu} \circledast  \boldsymbol{U})^k)\Big) &=0,\quad (t,x) \in Q_T,\\
  % \\
  % \label{init}
  % U^{k}(0,x)&=U_0^{k}(x), \quad x \in \R,
%   \end{split}
% \end{align} ,
% \,\quad (t,x) \in Q_T:= (0,T)\times\R, \\ 
% % \label{eq:umuli}
%  \boldsymbol{U}(0,x)&=\boldsymbol{U}_0(x), \quad x \in\R,
 % \end{split}
\label{sc}
 % \begin{split}
% \partial_t U^{k} +\partial_x \Big(f^k(U^k) \nu^k((\boldsymbol{\mu} \circledast  \boldsymbol{U})^k)\Big) &=0, \quad (t,x) \in Q_T,k\in\mathcal{N}\\
(\mu^{j,k}*U^j)(t,x)&:=\displaystyle\int_{\R} U^j(t,\xi)\mu^{j,k}(x-\xi)  \d \xi,
% \end{split}
\end{align}
as the radius of the temporal convolution kernel $\boldsymbol{\Gamma}$ tends to zero?  \item \label{b} Does it converge to the entropy solution of its ``nonlocal-time'' counterpart 
as the radius of the spatial convolution kernel $\boldsymbol{\mu}$ tends to zero?  
\item \label{c} Does it converge to the entropy solution of its local counterpart
\begin{align}\label{local}
\partial_t U^{k} + \partial_x \Big(f^k(U^k)\, \nu^k(\boldsymbol{U})\Big) = 0, \quad (t,x) \in Q_T,
\end{align}
as the radii of the temporal and spatial convolution kernels $\boldsymbol{\Gamma}$ and $\boldsymbol{\mu}$ tend to zero? 
\item \label{d} Do there exist finite volume approximations for \eqref{nlm}–\eqref{init} that are asymptotically compatible with any of the limiting passages described above? If so, can one quantify the corresponding rates of this asymptotic convergence?
\end{enumerate}
In this article, we would obtain uniform spatial $\bv$ bounds on $\boldsymbol{U}$ independent of $\|\Gamma^{j,k}\|_{L^\infty(\R)}$ in \S\ref{num}, using which, we would answer \ref{a} and corresponding \ref{d} affirmatively, thereby confirming the passage from the ``memory'' model to its ``memoryless'' counterpart in \S\ref{NLL}. 

The passage from the ``nonlocal space-time'' system \eqref{nlm}-\eqref{init} to the ``nonlocal-time'' setting \ref{b} is not addressed here since this yields a system with a flux that is local and is discontinuous in space; 
the well-posedness of such systems is largely open.

Lastly, the answer to \ref{c} remains largely open, with the exception of \cite{DHSS2023}, which addresses this issue for $N=1$ with a specific choice of $\Theta,$ and a linear flux $f$ via a relaxation scheme. 
In general, questions \ref{c} and \ref{d} with  $N=1, \boldsymbol{\Theta}=\boldsymbol{\mu}$ and for the specific choice for a linear $f,$ and $\mu$ a decreasing kernel have been investigated in recent years 
see, for instance, \cite{BS2020,BS2021,CCDKP2022,GNAL2021,CGES2021,CCS2019,FGKP2022,KP2019,CAL2020,FKG2018}, and  \cite{DH2024,NH2025} respectively. The case of a general $\mu$ and nonlinear $f$ remains open, to the best of our knowledge. {\color{black}However, for systems ($N>1$), questions \ref{c} and \ref{d} remain largely undeveloped and highly nontrivial. While recent works~\cite{AHV2023,AHV2023_1} prove that the nonlocal coupled system \eqref{nlm}–\eqref{init} is well posed for arbitrary $\bv$ initial data, the corresponding local system \eqref{local},\eqref{init} exhibits severe analytical difficulties and is, in general, ill-behaved with very limited well-posedness results:  existence for any $N$ with sufficiently small $\bv$ data~\cite{B2000,HR2015}, and  existence for $N=2$ with sufficiently small $L^{\infty}$ data~\cite{BMV2025}.}
 This substantial disparity makes question \ref{c} very delicate for $N>1$, 
and it remains an elusive open problem at the time of writing even for $\boldsymbol{\Theta}=\boldsymbol{\mu}$. Similarly, questions \ref{c} and, consequently, \ref{d} with  $\boldsymbol{\Theta}=\boldsymbol{\Gamma}$ for any $N\ge 1$ remains still unexplored.
Consequently, an affirmative answer to \ref{c}-\ref{d}, i.e., the complete passage for any general $\boldsymbol{\Theta}$ and for any nonzero integer $N$ from the ``nonlocal space-time'' system \eqref{nlm}-\eqref{init} to the local limit \eqref{local},\eqref{init} is difficult to expect and lies beyond the scope of this paper. 
% {\color{black}
% The remainder of the paper is organized as follows. In \S\ref{uni}, we establish uniqueness and continuous dependence with respect to the initial data for \eqref{nlm}–\eqref{init}, based on stability estimates for local scalar conservation laws. In \S\ref{num}, we propose a first-order numerical scheme for the approximation of the initial value problem and prove convergence of the approximate solutions to the unique entropy solution, thereby establishing existence. Taken together, these results yield the well-posedness of the problem. In \S\ref{NLL}, we analyze the dynamics in the presence of fading memory. In particular, we investigate the asymptotic behavior as the support of the temporal convolution kernel shrinks to zero. We prove that the unique entropy solutions of the space–time nonlocal conservation law converge to the entropy solution of the purely spatially nonlocal conservation law at the rate $\mathcal{O}(\sqrt{\delta})$, where $\delta$ denotes the radius of the time convolution. In addition, we show that the proposed finite volume approximations are asymptotically compatible with this memory-to-memoryless limit and derive error estimates of the order $\mathcal{O}(\sqrt{\delta} + \sqrt{\Delta x})$.}\\
% % Finally, numerical experiments supporting the theory of the article, are presented.}
% {\color{black}
% {Do we need more in intro?: Yes}}.\\
% The purpose of this work is to analyze conservation laws combining both effects, namely \emph{space--time nonlocal models with memory}. 
% We consider equations of the form
% \begin{equation}\label{eq:main}
% \partial_t u(t,x)
% + \int_{\mathbb{R}} \mu(x-\xi)
% \int_0^t \Gamma(t-\tau)\, f(u(\tau,\xi))\, d\tau d\xi
% =0,
% \end{equation}
% supplemented with initial data $u(0,x)=u_0(x)$. 
% Here $\mu$ is a spatial interaction kernel and $\Gamma$ is a temporal memory kernel. 
% Model \eqref{eq:main} unifies two distinct mechanisms:
% \begin{itemize}
% \item spatial nonlocal interactions acting over a finite horizon,
% \item hereditary (Volterra-type) temporal effects.
% \end{itemize}

% When $\Gamma$ converges to the Dirac distribution, equation \eqref{eq:main} formally reduces to a purely spatial nonlocal conservation law. 
% When, in addition, $\mu$ converges to a Dirac mass, one recovers the classical local conservation law
% \[
% \partial_t u + \partial_x f(u)=0.
% \]
% Thus, \eqref{eq:main} provides a natural multiscale framework interpolating between fully local dynamics and history-dependent nonlocal interactions.
% Space--time nonlocal conservation laws combine these two mechanisms: the evolution at a point depends on spatial averages of the state as well as on its past history. 
% Such models are particularly relevant when interactions occur over a finite spatial horizon and with delayed response, yielding a multiscale framework that interpolates between classical local conservation laws and hereditary hyperbolic systems.

% The combined space--time nonlocal structure generates new analytical challenges. 
% The flux depends on both the spatially distributed state and the entire past history of the solution, preventing a semigroup formulation and complicating compactness arguments. 
% In particular, obtaining uniform $\bv$ estimates that remain stable under singular limits of the kernels requires refined techniques.

% The main contributions of this paper are the following:
% \begin{itemize}
% \item We establish well-posedness of entropy solutions under minimal integrability assumptions on the temporal kernel.
% \item We derive uniform spatial $\bv$ bounds independent of $\|\Gamma\|_{L^\infty}
% $\item We rigorously justify the asymptotic limit in which the temporal kernel converges to the Dirac distribution, proving convergence of the associated evolution operators.\end{itemize}

% Our results provide a unified analytical framework for conservation laws with simultaneous spatial nonlocality and temporal memory, and they contribute to the understanding of singular kernel limits in hereditary hyperbolic problems.
The remainder of the paper is organized as follows. In \S\ref{uni}, we establish uniqueness and continuous dependence with respect to the initial data for \eqref{nlm}–\eqref{init}, based on stability estimates for local scalar conservation laws. In \S\ref{num}, we propose a first-order numerical scheme for the approximation of the initial value problem and prove convergence of the approximate solutions to the unique entropy solution, thereby establishing existence. Taken together, these results yield the well-posedness of the problem. In \S\ref{NLL}, we analyze the dynamics in the presence of fading memory, the memory-to-memoryless dynamics. In particular, we investigate the asymptotic behavior as the support of the temporal convolution kernel shrinks to zero. We prove that the unique entropy solutions of the space–time nonlocal conservation law converge to the entropy solution of the purely spatially nonlocal conservation law at the rate $\mathcal{O}(\sqrt{\delta})$, where $\delta$ denotes the radius of the time convolution. In addition, we show that the proposed finite volume approximations are asymptotically compatible with this memory-to-memoryless limit and derive error estimates of the order $\mathcal{O}(\sqrt{\delta} + \sqrt{\Delta x})$. Finally, in \S\ref{num1},  numerical experiments supporting the theory of the article are presented.
% \section{Introduction}

% Many real-world systems exhibit dynamics in which the state depends not only on the present configuration but also on its past history. Such memory effects arise naturally in damping in elastic media~\cite{CHR2007,c2008}, viscoelasticity~\cite{Dafermos1970,Dafermos1979}, fractional-in-time models~\cite{Podlubny1999}, gas transport in porous media~\cite{Clarkson1999,Shi2003}, and subsurface transport processes~\cite{Haggerty1995,Gooseff2003,Haggerty2002}. A prototypical scalar conservation law with memory takes the form
% \begin{equation}\label{eq:memory_general}
% \partial_t u
% + \partial_x \Big( f\big(u,\int_0^t u(\tau,x)\Gamma(t-\tau)\, d\tau \big) \Big)
% =0, \quad (t,x)\in (0,T)\times\mathbb{R},
% \end{equation}
% where $\Gamma$ is a temporal memory kernel. Despite their modeling relevance, the mathematical theory for such systems remains largely incomplete. The main difficulty stems from the temporal convolution, which introduces nonlocal dependence in time while typically reducing spatial regularity of the flux. This destroys the semigroup structure and prevents direct application of standard techniques for scalar conservation laws. As a consequence, stability and compactness arguments become significantly more delicate. Existing results~\cite{c2008,N2023,DHSS2023,P2014,liu2020,Dafermos1970,D1987,CC2007,DAF2012,CHR2007} address only special cases under additional structural assumptions on the flux.

% In contrast, conservation laws with purely spatial nonlocality,
% \begin{equation}\label{nls1}
% \partial_t u + \partial_x \Big(f\big(u,\int_{\mathbb{R}} u(t,\xi)\mu(x-\xi)\, d\xi \big)\Big)=0,
% \end{equation}
% have been extensively studied over the past decade. These models arise in crowd dynamics~\cite{CGL2012,ACG2015}, traffic flow~\cite{BG2016,BHL2023,FGKP2022,GR2019,AHV2023_1,AHV2024}, opinion dynamics~\cite{ANT2007}, sedimentation~\cite{BBKT2011}, granular media~\cite{AS2012}, conveyor systems~\cite{GHS+2014}, and related applications. Their analytical tractability is closely linked to their connection with local conservation laws, leading to a well-developed well-posedness theory; see, e.g.,~\cite{CK24,FGR2021,BFK2022,AV2023,FCV2023,KP2021,CG2019,KLS2018,,CHM2011,BHL2023,ACT2015,AG2016,CL2011,CNAP2022,CGL2024,CG2023,CM2015,CR2018,}.

% The present work combines these two frameworks by considering conservation laws with convolution kernels depending simultaneously on space and time. We study the initial-value problem for a coupled system of $N$ nonlocal conservation laws of the form
% \begin{align}
% \label{nlm}
% \partial_t U^{k} + \partial_x \Big(f^k(U^k)\,\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k)\Big) &= 0,
% \quad (t,x)\in (0,T)\times\mathbb{R}, \\
% \label{init}
% U^{k}(0,x) &= U_0^k(x),
% \end{align}
% for $k=1,\dots,N$, where the nonlocal operator $\boldsymbol{\Theta}\circledast \boldsymbol{U}$ couples all components through both spatial averaging and temporal memory.

% More precisely, the kernel is of separable form $\Theta^{j,k}(t,x)=\mu^{j,k}(x)\Gamma^{j,k}(t)$, so that the nonlocal term is given by
% \begin{equation}\label{mc}
% (\Theta^{i,k}*U^i)(t,x)
% := \int_0^t \int_{\mathbb{R}} U^i(\tau,\xi)\mu^{i,k}(x-\xi)\Gamma^{i,k}(t-\tau)\, d\xi d\tau.
% \end{equation}
% This structure introduces both spatial averaging over finite interaction horizons and temporal memory effects. Consequently, the flux at $(t,x)$ depends not only on the instantaneous value $U^k(t,x)$ but also on spatially distributed past states of all components. In applications, $\Gamma^{i,k}$ is typically decreasing, reflecting fading memory, although our analysis applies under more general regularity assumptions.

% From a modeling perspective, system~\eqref{nlm} couples multiple species through nonlocal interactions in both space and time. The resulting characteristic speeds depend on the full past history of the solution, leading to a strongly coupled, history-dependent hyperbolic system. This introduces new analytical difficulties beyond both classical conservation laws and spatially nonlocal models.

% While well-posedness for spatially nonlocal conservation laws is now relatively well understood, the extension to time-dependent kernels remains largely open, particularly in the multi-dimensional coupling setting $N>1$. Existing work using relaxation or special structures~\cite{DHSS2023} addresses only restricted scalar cases.

% In this paper, we establish existence and uniqueness of entropy solutions for~\eqref{nlm}--\eqref{init} in a general framework. A key step is the derivation of uniform spatial BV estimates independent of the temporal kernel, which allows us to adapt techniques from the spatially nonlocal setting.

% We then address asymptotic regimes associated with fading memory. Specifically, we study the limit in which the support of $\Gamma^{j,k}$ shrinks to zero, showing convergence of solutions of~\eqref{nlm} to the entropy solution of the purely spatially nonlocal system
% \begin{equation}\label{nls}
% \partial_t U^{k} + \partial_x \Big(f^k(U^k)\,\nu^k((\boldsymbol{\mu}\circledast \boldsymbol{U})^k)\Big)=0.
% \end{equation}
% We further establish quantitative convergence rates and prove that the proposed finite volume scheme is asymptotically compatible with this limit.

% We also briefly discuss other limiting regimes, including vanishing spatial interaction and the simultaneous local limit, highlighting that the latter remains largely open for systems due to the severe analytical challenges associated with the corresponding local coupling structure.

% Finally, numerical experiments are provided to support the theoretical findings.
\section{Definitions and notation}\label{def}
We will be using the following notations:
\begin{enumerate}
% \item 
 % \item $\norma{\boldsymbol{f}}_{(L^1(\R))^N}:=\displaystyle\sum\limits_{k\in\mathcal{N}}\norma{f^k}_{L^1(\R)}.$ 
    \item For $\boldsymbol{Z}:=(Z^k)_{k\in\mathcal{N}}\in \R^N,$ let $\norma{\boldsymbol{Z}}:=\displaystyle\sum\limits_{k\in\mathcal{N}}\abs{Z^k}$ denote the usual $1$-norm.
    \item 
$
\norma{\boldsymbol{\Theta}}_{(L^{\infty}(\overline{Q}_T))^{N^2}}:= \max\limits_{i,j\in\mathcal{N}} \norma{\Theta^{i,j}}_{L^{\infty}(\overline{Q}_T)}.
$
\item If $\boldsymbol{\mu}\in C^2(\R;\R^{N^2})=(\mu^{j,k})_{j,k\in\mathcal{N}}$, then $\boldsymbol{\mu}'=({\dot{\mu}}^{j,k})_{j,k\in\mathcal{N}}\in C^1(\R;\R^{N^2})$ and $\boldsymbol{\mu}''=({\ddot{\mu}}^{j,k})_{j,k\in\mathcal{N}} \in C(\R;\R^{N^2})$ denote the component-wise derivative and second derivative, respectively. 
   \item For $u: \overline{Q}_T\rightarrow \R,$ $\boldsymbol{U}:\overline{Q}_T \rightarrow \R^N$ 
  and $\tau>0$, 
\begin{align*}
|u|_{\lip_tL^1_x}&:=\sup_{0\leq t_1<t_2\leq T}\frac{\norma{u(t_1,\cdot)-u(t_2,\cdot)}_{L^1(\R)}}{|t_1-t_2|},\\
|\boldsymbol{U}|_{(\lip_tL^1_x)^N}&:=\max_{k\in\mathcal{N}}|U^k|_{\lip_tL^1_x}, \\  
|\boldsymbol{U}|_{(L^\infty_t\bv_x)^N}&:=\max_{k\in\mathcal{N}}\sup_{t\in[0,T]} TV(U^k(t,\dott)),\\  
\norma{\boldsymbol{U}}_{(L^{\infty}(\overline{Q}_T))^N}&:=\max_{k\in\mathcal{N}} \norma{U^k}_{L^{\infty}(\overline{Q}_T)}=1,\\ \gamma(\boldsymbol{U},\tau)&:= \max_{k\in\mathcal{N}}\sup_{\substack{
    \abs{t_1-t_2} \leq \tau\\  0\leq t_1\leq t_2\leq T }} \norma{U^k(t_1,\cdot)-U^k( t_2,\cdot)}_{L^1(\R)},\\ 
\norma{\boldsymbol{U}}_{(L^1(\overline{Q}_T))^N}&:=\sum\limits_{k\in\mathcal{N}}\norma{U^k}_{L^1(\overline{Q}_T)}.
\end{align*} 
\end{enumerate}
Since $f^k$ is nonlinear, there can be multiple weak solutions of \eqref{nlm}-\eqref{init}, like in a local hyperbolic conservation law. Hence, an entropy condition is required to single out the unique solution.
\begin{definition}\label{def:entropy}
    A function $\textbf{U} \in (C([0,T];L^1(\R;[0,1]))\cap L^{\infty}([0,T];\bv(\R)))^N$  is an entropy solution of \eqref{nlm}-\eqref{init} with initial data $\textbf{U}_0$
    % \in ((L^1 \cap \bv) (\R;[0,1]))^N,
    % $
if for each $(k,\alpha)\in \mathcal{N}\times\R$, and for all non-negative $\phi\in C_c^{\infty}([0,T)\times \R),$
\begin{multline} \label{kruz2}
\int_{Q_T}\left|U^k(t,x)- \alpha\right|\phi_t(t,x)  \d x \d t+\int_{\R} \left|U_0^k(x)- \alpha\right|\phi(0,x) \d x  \\ 
+ \int_{Q_T}\sgn ({U}^k(t,x)-\alpha) \nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x))
(f^k({U}^k(t,x))-f^k(\alpha))\phi_x(t,x) \d{x} \d{t}\\ 
 -\int_{Q_T} f^k(\alpha) (\sgn ({U}^k(t,x)-\alpha)) \partial_x\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x))\phi(t,x)\d{x} \d{t}\geq 0. 
\end{multline}
\end{definition}
\section{Uniqueness}\label{uni}
% \begin{definition}
%     A function $u\in C([0,T];L^1(\R;[0,1]))\cap L^{\infty}(\overline{Q}_T)$  is an entropy solution of the IVP~\eqref{IVP:eq}--\eqref{IVP:data} {\color{blue}with $U_{0}^k\in L^1(\R;[0,1])$}, 
% if for every $k\in\R,$ and for all non-negative $\phi\in C_c^{\infty}([0,T)\times \R)$,
% \begin{align} \label{kruz}
% \begin{split}
% &\int_{Q_T} |U^k(t,x)-\alpha|\phi_t\d t \d x \\&+\int_{Q_T}\sgn(U^k(t,x)-k) (f^k(U^k(t,x))-f^k(\alpha))\nu^k(\mathcal{U}^k(t,x))\phi_x \d t \d x\\ 
% &-\int_{Q_T} \sgn (U^k(t,x)-\alpha)f^k(\alpha)\partial_x(\nu^k(\mathcal{U}^k(t,x))\phi \d t \d x \\&  +\int_{\R} |U_{0}^k(x)-\alpha|\phi(0,x) \d x \geq 0,
% \end{split}
% \end{align}
% where for every $(t,x)\in \overline{Q}_T,$
% % \begin{align}\label{mc}
% %\begin{split}
%     $ \mathcal{U}^k(t,x)=(\Theta*u)(t,x).$
%      % \\  &=\displaystyle\int_0^t\int_{\R}U^k(\tau,x-\xi)\mu^{j,k}(\xi)\Gamma^{j,k}(t-\tau) \d \tau \d \xi.
% %\end{split}
% % \end{align}
% \end{definition}
% \item 
We now prove that any two entropy solutions of the IVP \eqref{nlm}-\eqref{init} are equal, more precisely, we have the following result:
% \item $|u|_{\lip_t L^1_x}:=\sup_{0\leq t_1<t_2\leq T}\frac{\norma{U^k(t_1,\dott)-U^k(t_2,\dott)}_{L^1(\R)}}{|t_1-t_2|}.$ 
    % \item $K:=\{u:\overline{Q}_T \rightarrow \R: ||u||_{L^{\infty}(\overline{Q}_T)}+|u|_{L^\infty_t \operatorname{BV}_x}<\infty\}.$
    % \item$\Gamma^{j,k}(U^k,\sigma)=\sup_{\substack{
    % 0\leq t_1\leq t_2\leq T \\ \abs{t_1-t_2} \leq \sigma}} \norma{U^k(t_1)-U^k(t_2)}_{L^(\R)}.$ 
  % \item$\Gamma^{j,k}(U^k,\sigma):=\sup_{\substack{
    % \abs{t_1-t_2} \leq \sigma\\  0\leq t_1< t_2 \leq T }} \norma{U^k(t_1,\dott)-U^k(t_2,\dott)}_{L^1(\R)}.$
% \end{enumerate}/

\begin{theorem}[Uniqueness]
For any time $T>0,$ let $\boldsymbol{U,V}$ 
be the entropy solutions of the IVP for the system \eqref{nlm}-\eqref{init}
  with initial data $\boldsymbol{U}_0,\boldsymbol{V}_0$, respectively. Then, the following holds:
\begin{align*}
\begin{split}
\norma{\boldsymbol{U}(T,\dott)-\boldsymbol{V}(T,\dott)}_{(L^1(\R))^N}&\leq
\norma{\boldsymbol{U}_0-\boldsymbol{V}_0}_{(L^1(\R))^N}\\& +\mathcal{C} \sum\limits_{k\in\mathcal{N}}\int_0^T \norma{U^k(\tau,\cdot)-V^k(\tau,\cdot)}_{L^1(\R)} \d \tau,
\end{split}
\end{align*}   \text{where  }
 \begin{align*}
\mathcal{C}&= NT\abs{\boldsymbol{f}}_{(\operatorname{Lip}(\R))^N}|\boldsymbol{\nu}|_{(\operatorname{Lip}(\R^N))^N}\norma{\boldsymbol{\Theta}}_{{(L^{\infty}(\overline{Q}_T))}^{N^2}}|\boldsymbol{U}|_{(L^\infty_t\bv_x)^N}\\
&\quad+NT\abs{\boldsymbol{f}}_{(\operatorname{Lip}(\R))^N}{\norma{\boldsymbol{U}_0}_{{(L^1(\R))}^N}}\norma{{\color{black}\nabla }\boldsymbol{\nu}}_{(L^{\infty}(\R^N))^{N^2}}\norma{\boldsymbol{\Gamma}}_{(L^{\infty}(\R^{+}))^{N^2}}\norma{\boldsymbol{\mu}'}_{(L^{\infty}(\R))^{N^2}}\\
&\quad+NT\abs{\boldsymbol{f}}_{(\operatorname{Lip}(\R))^N}{\norma{\boldsymbol{U}_0}_{{(L^1(\R))}^N}}\norma{\boldsymbol{V}}_{(L^{1}(Q_T))^N} \norma{\boldsymbol{\Gamma}}_{(L^{\infty}(\R^{+}))^{N^2}}\norma{\boldsymbol{\mu}'}_{(L^{\infty}(\R))^{N^2}} \\&\qquad\times{\color{black}\norma{\operatorname{Hess}\boldsymbol{\nu}}}_{(L^{\infty}(\R^{N}))^{N^3}}\norma{\boldsymbol{\Theta}}_{{(L^{\infty}(\overline{Q}_T))}^{N^2}}.\end{align*}
 In particular, if $\boldsymbol{U}_0=\boldsymbol{V}_0,$ then $\boldsymbol{U}=\boldsymbol{V}$ a.e.~in $\overline{Q}_T$.
\end{theorem}
\begin{proof}
Let $(t,x)\in Q_T$. Since for each $k\in\mathcal{N}, U^k$ and $V^k$ are entropy solutions of \eqref{nlm}-\eqref{init},
using the continuous dependence estimates for conservation laws with smooth coefficients (see \cite[Theorem~1.3]{KR2003}) and following similar steps as in \cite[Theorem~4.1]{BBKT2011}, \cite[Theorem~2]{BG2016},  we have:
\begin{align*}
&\norma{U^k(T,\dott)-V^k(T,\dott)}_{L^1(\R)}\leq
\norma{U^k_0-V^k_0}_{L^1(\R)} + \abs{f^k}_{\lip(\R)}(\mathcal{I}_1^k+\mathcal{I}_2^k),
\end{align*}
where
\begin{align}\label{cont_dependennce}
\begin{split}
&\mathcal{I}_1^k:=\int_0^T\int_{\R}\abs{U^k_x(t,x)}  \abs{\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x))-\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{V})^k(t,x))} \d x \d\tau,\\ &\mathcal{I}_2^k:=\int_0^T\int_{\R} \abs{U^k(t,x)}  \abs{\partial_x(\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x)))-\partial_x(\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{V})^k(t,x)))} \d x \d\tau.
    \end{split}
\end{align}
% We first consider $\mathcal{I}_1^k.$
 Note that  
 \begin{align} \label{U}
\begin{split}
&\abs{\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x))-\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{V})^k(t,x))}\\
&\le|\nu^k|_{\operatorname{Lip}(\R^N)}\norma{(\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x)-(\boldsymbol{\Theta}\circledast \boldsymbol{V})^k(t,x)}\\
&=|\nu^k|_{\operatorname{Lip}(\R^N)}\sum\limits_{j\in\mathcal{N}}\int_0^t\int_{\R}
\abs{U^j(\tau,\xi)-V^j(\tau,\xi)}\mu^{j,k}(x-\xi)\Gamma^{j,k}(t-\tau) \d \tau \d \xi\\
 &\le|\nu^k|_{\operatorname{Lip}(\R^N)}\norma{\boldsymbol{\Theta}}_{{(L^{\infty}(\overline{Q}_T))}^{N^2}}\sum\limits_{k\in\mathcal{N}}\int_0^t\norma{U^k(\tau,\cdot)-V^k(\tau,\cdot)}_{L^1(\R)} \d \tau.
 \end{split}
 \end{align}
 Also, for $\boldsymbol{Z}=\boldsymbol{U},\boldsymbol{V}$,
\begin{align*}
&\nabla\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{Z})^k(t,x))\dott \partial_x((\boldsymbol{\Theta}\circledast \boldsymbol{Z})^k)(t,x)\\&\quad=\sum\limits_{j\in\mathcal{N}}\partial_{j}\nu^{k}\!\left((\boldsymbol{\Theta}\circledast \boldsymbol{Z})^k(t,x)\right)\,
\int_{0}^{t}\!\int_{\mathbb{R}}
Z^{j}(\tau,\xi)\,\dot{\mu}^{j,k}(x-\xi) \d \xi \d \tau,\end{align*}
and hence,
% Also,
\begin{align*}
&\nabla\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x))\dott \partial_x((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k)(t,x)-\nabla\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{V})^k(t,x))\dott \partial_x((\boldsymbol{\Theta}\circledast \boldsymbol{V})^k)(t,x)\\
&=\sum\limits_{j\in\mathcal{N}}\partial_{j}\nu^{k}\!\left((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x)\right)\,
\int_{0}^{t}\!\int_{\mathbb{R}}
(U^{j}(\tau,\xi)-V^{j}(\tau,\xi))\,\dot{\mu}^{j,k}(x-\xi)\,
\Gamma^{j,k}(t-\tau)\,d\xi\,d\tau\\
&\quad+\sum\limits_{j\in\mathcal{N}}(\partial_{j}\nu^{k}\!\left((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x)\right)-\partial_{j}\nu^{k}\!\left((\boldsymbol{\Theta}\circledast \boldsymbol{V})^k(t,x)\right)\,
\int_0^t \int_{\mathbb{R}}V^{j}(\tau,\xi))\,\dot{\mu}^{j,k}(x-\xi)\,
\Gamma^{j,k}(t-\tau)\,d\xi\,d\tau\\
&=\mathcal{I}_{21}^k+\mathcal{I}_{22}^k.
\end{align*}
Clearly, with $\mathcal{C}_2:=\norma{{\color{black}\nabla }\boldsymbol{\nu}}_{(L^{\infty}(\R^N))^{N^2}}\norma{\boldsymbol{\Gamma}}_{(L^{\infty}(\R^{+}))^{N^2}}\norma{\boldsymbol{\mu}'}_{(L^{\infty}(\R))^{N^2}}$, \begin{align}
\label{I21}
\mathcal{I}_{21}^k
&\le \mathcal{C}_2\sum\limits_{k\in\mathcal{N}}\int_0^T\norma{U^k(\tau,\cdot)-V^k(\tau,\cdot)}_{L^1(\R)} \d \tau.
\end{align}
Further, using \eqref{U} and a similar estimate with $\partial_j\nu^k,$ for every $j\in\mathcal{N}$, we get:
\begin{align*}
&\abs{\partial_{j}\nu^{k}\!\left((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x)\right)-\partial_{j}\nu^{k}\!\left((\boldsymbol{\Theta}\circledast \boldsymbol{V})^k(t,x)\right)}\\&\le \norma{\operatorname{Hess}\nu^k}_{(L^{\infty}(\R^{N}))^{N^2}}\norma{\boldsymbol{\Theta}}_{{(L^{\infty}(\overline{Q}_T))}^{N^2}}\sum\limits_{k\in\mathcal{N}}\int_0^T\norma{U^k(\tau,\cdot)-V^k(\tau,\cdot)}_{L^1(\R)} \d \tau,
\end{align*} and hence with, $$\mathcal{C}_3:=\norma{\boldsymbol{V}}_{(L^{1}(Q_T))^N} \norma{\boldsymbol{\Gamma}}_{(L^{\infty}(\R^{+}))^{N^2}}\norma{\boldsymbol{\mu}'}_{(L^{\infty}(\R))^{N^2}} {\color{black}\norma{\operatorname{Hess}\boldsymbol{\nu}}}_{(L^{\infty}(\R^{N}))^{N^3}}\norma{\boldsymbol{\Theta}}_{{(L^{\infty}(\overline{Q}_T))}^{N^2}},$$ \begin{align}\label{I22}
\mathcal{I}_{22}^k
&\le \mathcal{C}_3\sum\limits_{k\in\mathcal{N}}\int_0^T\norma{U^k(\tau,\cdot)-V^k(\tau,\cdot)}_{L^1(\R)} \d \tau.
\end{align} 
 Consequently, using \eqref{U}-\eqref{I22}, we have
\begin{align} \label{U1}
\begin{split}
\mathcal{I}_1^k
&\le\mathcal{C}_1\sum\limits_{k\in\mathcal{N}}\int_0^T\norma{U^k(\tau,\cdot)-V^k(\tau,\cdot)}_{L^1(\R)} \d \tau,\\
%  \end{split}
%  \end{align}
% and
% Finally combining ,
% \begin{align} \label{Ux}
% \begin{split}
\mathcal{I}_2^k& \leq \int_{0}^{T}\int_{\R}\abs{U^k(\tau,x)} (\mathcal{I}_{21}^k+\mathcal{I}_{22}^k) \d x \d \tau
 \leq  \mathcal{C}_4\sum\limits_{k\in\mathcal{N}}\int_0^T\norma{U^k(\tau,\cdot)-V^k(\tau,\cdot)}_{L^1(\R)} \d \tau.
\end{split},
\end{align}
where $\mathcal{C}_1:=T |\boldsymbol{\nu}|_{(\operatorname{Lip}(\R^N))^N}\norma{\boldsymbol{\Theta}}_{{(L^{\infty}(\overline{Q}_T))}^{N^2}}|\boldsymbol{U}|_{(L^\infty_t\bv_x)^N}$, and $\mathcal{C}_4:=T{\norma{\boldsymbol{U}_0}_{{(L^1(\R))}^N}}(\mathcal{C}_2+\mathcal{C}_3).$
Finally, inserting the above estimates in \eqref{cont_dependennce} and summing over $k\in\mathcal{N}$, we have the result.
\end{proof}


\section{Numerical approximations and their convergence}\label{num}
For $\Delta x, \Delta t>0,$ and $\lambda:=\Delta t/\Delta x,$ consider equidistant spatial grid points $x_i:=i\Delta x$ for $i\in \Z,$ and let $\chi_i(x)$ denote the indicator function of $C_i:=[x_{i-1/2}, x_{i+1/2})$, where $x_{i+1/2}=\frac{1}{2}(x_i+x_{i+1})$. Further, let $t^n:=n\Delta t$ 
for integers in $\mathcal{N}_T:=\{0, \ldots, N_T\}$, such that $T=N_T \D t$ denote the temporal grid points, and let
$\chi^n(t)$ denote the indicator function of $C^{n}:=[t^n,t^{n+1})$. For every $k\in\mathcal{N}$, we approximate the initial data \eqref{init}, according to:
\begin{equation*}
U^{k,\Delta}_0(x):=\sum\limits_{i\in\Z}\chi_i(x)U^{k,0}_i\quad \mbox{where }U^{k,0}_i=\frac{1}{\Delta x^2}\int_{C_i}U_{0}^k(x)\d x, \quad i\in \Z,
\end{equation*}
and define a piecewise constant approximate solution $U^{k,\Delta}$ to~\eqref{nlm}-\eqref{init}
by:
$$
  U^{k,\Delta} (t,x) =  U^{k,n+1}_{i}
  \mbox{ for } 
(t,x)\in {C}^{n}\times C_i, (i,n)\in \Z\times\mathcal{N}_T. 
$$
For every $(i,k,n)\in \Z\times\mathcal{N}\times\mathcal{N}_T$, $U^{k,n}_{i}$ is defined via the following marching formula:
\begin{align}
\begin{split}U^{k,n}_i&=H^k(\nu^k(\boldsymbol{c}^{k,n-1}_{i-1/2}),\nu^k(\boldsymbol{c}^{k,n-1}_{i+1/2}),U_{i-1}^{k,n},U_i^{k,n-1},U_{i+1}^{k,n-1})
    \\  
    & := 
   U^{k,n-1}_i- \lambda \big[
    \mathcal{F}^k(\nu^k(\boldsymbol{c}^{k,n-1}_{i+1/2}),U_i^{k,n-1},U_{i+1}^{k,n})
    - 
    \mathcal{F}^k(\nu^k(\boldsymbol{c}^{k,n-1}_{i-1/2}),U_{i-1}^{k,n-1},U_{i}^{k,n})
     \big]\\ 
     \label{scheme2}
     &:=U^{k,n-1}_i- \lambda \bigl[
    \mathcal{F}^{k,n}_{i+1/2} (U_i^{k,n-1},U_{i+1}^{k,n-1})
    - 
\mathcal{F}^{k,n-1}_{i-1/2} (U_{i-1}^{k,n-1},U_{i}^{k,n})
     \bigr].
     \end{split}\end{align}Here,  $\boldsymbol{c}_{i+1/2}^{k,n}:= \left(c_{i+1/2}^{s,k,n}\right)_{s\in \mathcal{N}}$ and 
$\mathcal{F}^k(\nu^k(\boldsymbol{c}^{k,n}_{i+1/2}),U_i^{k,n},U_{i+1}^{k,n})
    $ denotes the numerical approximation of the flux $f^k(U^k)\nu^k((\boldsymbol{\Theta}\circledast  \boldsymbol{U})^k)$ at $(t^n,x_{i+1/2})$ for $(k,i,n)\in \mathcal{N}\times\Z\times\mathcal{N}_T$, where for every $s,k\in \mathcal{N}$, 
\begin{align*}c_{i+1/2}^{s,k,n}&:=\Delta x \D t \sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{s,k,n-m}_{i+1/2-p} U^{s,m}_{p}=\Delta x \D t \sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{s,k,m}_{i+1/2-p} U^{s,n-m}_{p}\end{align*} approximates $\int_0^{t^n}\int_{\R}\Theta^{s,k}(x_{i+1/2}-\xi,t^n-\tau) U^{s,\D}(\tau,\xi )\d \xi \d \tau$. 

% {${\color{red}=\displaystyle\int_0^{t^n}\int_{\R}\Theta^{s,k}(x_{i+1/2}-\xi,\tau) U^{s,\D}(t^n-\tau,\xi )\d \xi \d \tau}$,Should we keep last line}
 Further, $\Theta_p^{j,k,s}=\mu^{j,k,p} \Gamma^{j,k,s},$ with $\mu^{j,k,p}$ and $\Gamma^{j,k,s}$ as the integral averages of $\mu^{j,k}$ and $\Gamma^{j,k}$ over $C_p$ and $C_s$ respectively.
In general, $\mathcal{F}^k$ can be defined as an appropriate nonlocal extension of any monotone numerical flux, meant for local conservation laws, for example,
% \begin{enumerate}
    % \item \textbf{Lax--Friedrichs type flux:} 
    % For any  define
\begin{equation*}
  \mathcal{F}^k(a_1,a_2,a_3)
   = 
  \frac{a_1}{2}\Big( f^k(a_2)
    +
    f^k(a_3)\Big)
  -
  \beta\frac{(a_3-a_2)}{2\, \lambda}, \beta\in (1, 2),
\end{equation*} is an extension of Lax-Friedrich's flux. This flux will be used in the sequel,
% {how to choose $\alpha$?} 
where  $\Delta t$ is chosen in order to satisfy
the CFL condition
\begin{equation}\label{CFL_LF}
   \lambda \le \frac{\min(1, 4-6\beta,6\beta)}{1+12\abs{\boldsymbol{f}}_{(\lip(\R))^N}\norma{\boldsymbol{\nu}}_{(L^\infty(\R^N))^N}}.\end{equation}
% \item \textbf{Godunov type flux:} {\color{blue}If additionally $\boldsymbol{\nu}\ge0,$ the nonlocal version of the standard Godunov Flux can also be defined as:},
% \begin{equation*}
% \mathcal{F}_{\rm Godunov}(a_1,a_2,a_3)= a_1 F_{\rm Godunov}(a_2,a_3),
% \end{equation*} 
% where the function $F_{\rm Godunov}$ is the Godunov flux for the corresponding local conservation law $U^k_t+f^k(U^k)_x=0$, i.e.,
% \begin{equation*}
% F_{God}(a_2,a_3)= 
% \begin{cases}
% \min_{w \in [a_2,a_3]} f^k(w), \quad & \text{if } a_2\leq a_3,\\
% \max_{w \in [a_3,a_2]} f^k(w), \quad & \text{if } a_2\geq a_3,
% \end{cases} 
% \end{equation*}
% and  $\Delta t$ is chosen in order to satisfy
% the CFL condition
% \begin{equation}\label{CFL_God}
%    \lambda \abs{\boldsymbol{f}}_{(\lip(\R))^N}\norma{\boldsymbol{\nu}}_{(L^\infty(\R^N))^N}\leq \frac16.
%    \end{equation}
% % \end{enumerate}{\color{blue}

% We now show that the numerical approximations $U^{k,\Delta}$ satisfy the expected physical properties. 
% To establish these properties, we
% need the following lemma on the convolution terms $c$. 

\begin{remark}\normalfont
The choice of $\Gamma^{j,k,s}$ as the integral average will play a crucial role in proving the asymptotic compatibility in Section~\ref{NLL}. However, the convergence of the finite volume schemes,  i.e., the following stability estimates (cf.~Lemma~\ref{stability}) and the convergence  (cf.~Theorem~\ref{convergence})--hold for the pointwise evaluation approximation of $\boldsymbol{\Gamma}$ at the cell center as well.
\end{remark}




% We now establish the $L^{\infty}$ bounds.
%   \begin{lemma}[$L^{\infty}$ bound]
%   \label{lem:Linfty}
%   Let~~\eqref{CFL_LF}
%   hold. Fix an initial datum ${U_{0}^k} \in (L^1  \cap \operatorname{BV})
%   (\R;{[0,\infty)})$. Then, the approximate solution ${U^{k,\Delta}}$
%   defined by the {marching formula}~\eqref{scheme2} satisfies for all $t \in
%   {\R^+}$,
%   \begin{equation}
%     \label{eq:8}
%     \norma{ {U^{k,\Delta}} (t)}_{L^{1}(\R)}
%     \leq
%     \mathcal{K}_4\exp(\mathcal{K}_3 \, t ) \,
%     \norma{{U^{k,\Delta}(0)}}_{L^{\infty}(\R)} \, ,
%   \end{equation}
%   with {\begin{equation*}
%  \mathcal{K}_3
%     =
%     \mathcal{C}_5^k{\color{black}\Delta t}\abs{f^k}_{\lip(\R)}
%      { \norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}}. 
%   \end{equation*}}
% \end{lemma}
% \begin{proof}
% %\begin{proofof}{Lemma~\ref{lem:Linfty}} Consider the case $i<0.$
% {Let $i\in \Z$ and $n  \in\mathcal{N}_T$. Note that},
%   \begin{align}
%     & 
%     \mathcal{F}^{k,n}_{{i+1/2}} (U_i^{k,n},U_i^{k,n})
%     -
%     \mathcal{F}^{k,n}_{{i-1/2}} (U_i^{k,n},U_i^{k,n})
%     \nonumber
%     \\
%     & = 
%   f^k(U_i^{k,n})\left(\nu^k(c_{{i+1/2}}^n)
%     -
%     \nu^k(c_{{i-1/2}}^n)\right)
%     \nonumber
%     \\
%     & \leq 
%    \abs{f^k}_{\lip(\R)}\abs{U_{i}^{k,n}}
%      { \norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}}     \mathcal{C}_5^k \Delta x .
%     \label{eq:bound1}
%   \end{align}
%   Now, using Lemma \ref{lem:L1}, \eqref{eq:bound1} in~\eqref{2.9}, we get
%   \begin{align*}
%     \modulo{ U_{i}^{n+1}}
%     & \leq 
%     (1-a^{k,n}_{{i-1/2}}-b^{k,n}_{{i+1/2}} ) U_i^{k,n}
%     +
%      a^{k,n}_{{i-1/2}} U_{i-1}^{k,n}
%     \\
%     & 
%     \quad
%     +
%      b^{k,n}_{{i+1/2}}U_{i+1}^{k,n}
%     +
%      \abs{f^k}_{\lip(\R)}U_{i}^{k,n}
%      { \norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}}     \mathcal{C}_5^k \Delta t
%     \\
%     & \leq 
%     (1-a^{k,n}_{{i-1/2}}-b^{k,n}_{{i+1/2}}) \norma{ {U^{k,\Delta}}(t^n)}_{L^{\infty}(\R)}
%     +
%      a^{k,n}_{{i-1/2}} \norma{ {U^{k,\Delta}}(t^n)}_{L^{\infty}(\R)}
%     \\
%     & 
%     \quad
%     +
%     b^{k,n}_{{i+1/2}} {\norma{{U^{k,\Delta}}(t^n)}_{L^{\infty}(\R)}}
%     + {\abs{f^k}_{\lip(\R)}}
%      { \norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}}     \mathcal{C}_5^k \Delta t{\norma{{U^{k,\Delta}}(t^n)}_{L^{\infty}(\R)}}
%     \\
%     & \leq 
%     {\norma{{U^{k,\Delta}}(t^n)}_{L^{\infty}(\R)}}
%     \left(
%       1
%       +
%       \mathcal{C}_5^k\Delta t\abs{f^k}_{\lip(\R)}
%     { \norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}} 
%     \right)\,.
%   \end{align*}
% {Consequently, with $\mathcal{K}_3=\mathcal{C}_5^k\abs{f^k}_{\lip(\R)}
%     { \norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}}$, we have}
%   \begin{align*}
%     \norma{{U^{k,\Delta}}(t^{n+1})}_{L^{\infty}(\R)}
%    &\leq
%     \left(
%       1
%       +
%     \mathcal{K}_3 \Delta t
%     \right) {\norma{{U^{k,\Delta}}(t^n)}_{L^{\infty}(\R)}} \,
% \\&\le \exp(\mathcal{K}_3\Delta t){\norma{{U^{k,\Delta}}(t^n)}_{L^{\infty}(\R)}}\\
% &\le \exp(\mathcal{K}_3(n+1)\Delta t)\norma{{U^{k,\Delta}(0)}}_{L^{\infty}(\R)},
%  \end{align*}
% {\color{black} so that for $0 \leq n \leq N,$} 
%   \begin{displaymath}  \norma{{U^{k,\Delta}}(t^n)}_{L^{\infty}(\R)}
%     \leq
%    {\norma{{U^{k,\Delta}(0)}}_{L^{\infty}(\R)}}
%     \exp(\mathcal{K}_3t^n)
%   \end{displaymath}
%   completing the proof.
%   \end{proof}
% Let $(i,n) \in \Z \times \mathcal{N}_T.$ 
\begin{lemma}\label{stability}Let $(j,i,k,n,t)\in\mathcal{N}\times\Z \times \mathcal{N}\times \mathcal{N}_T\times\R^{+}$ and let the CFL condition~\eqref{CFL_LF} hold. 
% Fix an initial datum
%   $U_{0}^k \in (L^1  \, \cap \, \operatorname{BV}) (\R ;{[0,1]})$.
The numerical approximations generated by the above marching formula satisfy:
\begin{enumerate}[label=(\alph*)]
 \item \label{lem:monotone} [Monotonicity] For a given fixed sequence
$\boldsymbol{c}_{i+1/2}^{n},$ $H^k$ is increasing in the last three arguments.
\item \label{Pos} [Invariant region principle]  
$0\leq U^{k,n}_i \leq 1.$
   \item \label{cons} [Conservation] 
$\sum\limits_{i\in \Z}U_i^{k,n} =  \sum\limits_{i\in \Z}U_i^{k,0}.$
\item \label{lem:L1} [$L^1$ bound]
% For $t \in {\R^+}$,
%   \begin{displaymath}
    ${\norma{ {U^{k,\Delta}} (t)}_{L^1(\R)}} = {\norma{ {U^{k,\Delta}} (0)}_{L^1(\R)}}.$
  % \end{displaymath}
% where 
 % \begin{align*}
% &\sum\limits_i
% \Big|
% (c^{j,k,n}_{i+1/2}-c^{j,k,n}_{i-1/2})
% -
% (c^{j,k,n-1}_{i+1/2}-c^{j,k,n-1}_{i-1/2})
% \Big|
% % \le
% % \Delta x
% % \sum\limits_{m=0}^{n-1}
% % \big(G^{j,k,n-m}_\delta-G^{j,k,n-1-m}_\delta\big)
% % \sum\limits_{i,p}
% % \big|\mu^{j,k}_{i+1/2-p,\delta}-\mu^{j,k}_{i-1/2-p,\delta}\big|
% % |\Delta U^{j,m}_{p,\delta}|\\
% \le
% \mathcal{C}_7^k\Delta x\sum\limits_{p} |\Delta U^{j,m}_{p}|,
% % \end{align*}
%     \end{align}
% \vspace{-8mm}
% \begin{align*}
% \text{where} \,\, \mathcal{C}_5^k&=\norma{U_{0}^k}_{L^1(\R)}\norma{\dot{\mu}^{j,k}}_{L^\infty(\R)}\norma{\Gamma^{j,k}}_{L^1(\R^+)}  \text{ and }\\ .
% \end{align*}

% \end{enumerate}
% end{lemma}

% \begin{lemma}\label{lem:BV}
\item \label{lem:BV}[ $\operatorname{BV}$ estimate] 
% For every $n\in\mathcal{N}_T,$ and for all $t \in c^{j,k,n}$,% the approximations
% defined by the {marching formula}~\eqref{scheme2} satisfy
%    \begin{eqnarray*}
%        \sum\limits_{i\in\Z}|\Delta_x^+(U_i^{k,n+1})|&\le&  \sum\limits_{i\in\Z}|(U_{i+1}^{k,n}-U_{i}^{k,n})|(1+\Delta t \mathcal{C}_7^k)+\Delta t \mathcal{C}_8^k
%     \end{eqnarray*}
% or equivalently,

    % \label{lem:BV}
    % for all $n$, for all $t \in \left(t^n, t^{n+1}\right),$
    % \begin{eqnarray}\label{BV:su}
    %   \sum\limits_{i\in\mathbb{Z}}
    %     \modulo{\Delta_x^+{(U_i^{k,n})}} 
    %       \leq 
    %  \exp(\mathcal{C}_7^kt)\sum\limits_{i\in\Z}\abs{\Delta_x^+{(U_{i}^{0})}}  + \frac{\exp(\mathcal{C}_7^kt)-1}{\mathcal{C}_7^k}\mathcal{C}_8^k
    %     ,
    % \end{eqnarray} and consequently,
  %  \vspace{-8mm}
    \begin{align*}
    \sum\limits_{i\in\mathbb{Z}}
        \modulo{U_{i+1}^{k,n}-U_i^{k,n}} 
          \leq\left(
\exp(\mathcal{C}_7^kt)\sum\limits_{i\in\Z}\abs{U_{i+1}^{k,0}-U_i^{k,0}}  + \frac{\exp(\mathcal{C}_7^kt)-1}{\mathcal{C}_7^k}\mathcal{C}_8^k\right),
\end{align*}
%\vspace{-2mm}
where
\begin{align*}  
\mathcal{C}_7^k&=\mathcal{C}_5^k \abs{f^k}_{\lip(\R)}  { \norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}},\\
\mathcal{C}_8^k&=\mathcal{C}_6^k\abs{f^k}_{\lip(\R)}\norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}\norma{U_{0}^k}_{L^1(\R)}{+2(\mathcal{C}^k_5)^2\abs{f^k}_{\lip(\R)}\abs{{\color{black}\nabla }{\nu^k}}_{(\lip(\R^N))^{N}}}\norma{U_{0}^k}_{L^1(\R)}.
      \end{align*}
      \item \label{lem:L1t}[Time Estimate]
For $m>n\in \mathcal{N}_T,$ we have the following time estimate:
\begin{align*}
\Delta x\sum\limits_{i\in \mathbb{Z}} \abs{U_i^{k,m}-U_i^{k,n}} \leq \mathcal{C}_9^k \Delta t (m-n),
\end{align*}
where $\mathcal{C}_9^k$ depends on 
  $\sum\limits_{i\in\mathbb{Z}}
        \modulo{U_{i+1}^{k,n}-U_{i}^{k,n}} ,\norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}},\norma{U_{0}^k}_{L^1(\R)},\abs{\mu^{j,k}}_{\operatorname{BV}(\R)},$\\ $  \norma{\Gamma^{j,k}}_{L^1(\R^+)}$ and is independent of $\delta$. 
        \item 
  \label{lem:entropy}[Discrete entropy condition]
% Then,
%   the approximate solution ${U^{k,\Delta}}$ defined by the {marching formula}~\eqref{scheme2}
For all $\alpha\in \R,$  we have
  % the discrete entropy inequality
 \begin{align*} 
 \begin{split}
% \label{eq:discrete_entropy}
 &\modulo{U_i^{k,n+1}-\alpha}-\modulo{U_i^{k,n}- \alpha}+\lambda\left({{G^{k,n}_{{i+1/2}}}(U_i^{k,n} ,U_{i+1}^{k,n})}-G^{k,n}_{{i-1/2}}(U_{i-1}^{k,n} ,U_i^{k,n})\right)\\
 &\quad \quad +\lambda\sgn(U_i^{k,n+1}-\alpha)f^k(\alpha)(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n}))\le 0,
 \end{split}
 \end{align*}
 %\vspace{-5mm}
 \begin{flalign*}&\text{where  }
{G^{k,n}_{{i+1/2}}}{(a,b)}=\mathcal{F}^{k,n}_{{i+1/2}}\left({\max(a,\alpha)},\,{\max(b,\alpha)}\right)
  -
  \mathcal{F}^{k,n}_{{i+1/2}}\left({\min(a,\alpha)},\,{\min(b,\alpha)}\right).&
\end{flalign*} 
 \item \label{eq:c_i+1/2} The convolution terms $\boldsymbol{c}$ satisfy the following bounds:
 \begin{align} \label{eq:c1}
&0 \leq {c}^{j,k,n}_{i+1/2} \leq 1,
\end{align}
\begin{align}
\label{eq:c2}
  &  | c^{j,k,n}_{i+1/2} - c^{j,k,n}_{i-1/2}|
    \leq 
    \mathcal{C}_5^k\Delta x,     \end{align}
     where $\mathcal{C}_5^k=\norma{U_{0}^k}_{L^1(\R)}\norma{\dot{\mu}^{j,k}}_{L^\infty(\R)}\norma{\Gamma^{j,k}}_{L^1(\R^+)},$  
     
    \begin{align}\label{eq:c3} &
    |c^{j,k,n}_{i+3/2} - 2c^{j,k,n}_{i+1/2}+c^{j,k,n}_{i-1/2}|
    \leq 
 \mathcal{C}_6^k\, \Delta x^{2},
 \end{align} 
 where $\mathcal{C}_6^k=2\norma{U_{0}^k}_{L^1(\R)} {\norma{\ddot{\mu}^{j,k}}_{L^{\infty}(\R)}} \norma{\Gamma^{j,k}}_{L^1(\R^+)}.$
 
% \end{lemma}
      \end{enumerate}
    \end{lemma} 
    % Since $f^k(1)=f^k(0)=0$, for any given sequence
% $\{\boldsymbol{c}_{i+1/2}^{k,n}\}_{(k,i,n)\in \mathcal{N}\times\Z\times\mathcal{N}_T}$, we have
% % $H(\dott,\dott,0,0,0)=0=H(\dott,\dott,1,1,1),$ which proves the claim \ref{Pos}-\ref{cons}.
% The proof of \ref{lem:L1} follows by a standard computation, see for example \cite[Lem.~2.4]{ACT2015}.
% Now, the result follows from the monotonicity of $H$ in the last three arguments from Lem.~ \ref{lem:monotone}.
%   The proof of  claim \ref{eq:c_i+1/2} follows by repeating the arguments of \cite[Prop.~2.8]{ACT2015} and \cite[Lem.~A.2]{ACG2015} in every component of the vector $\boldsymbol{c}_{i+1/2}^{k,n}:$
% Since $0\le \Delta x \D t \sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i+1/2-p} \leq 1 $ and for every $m\le n\in \mathcal{N}_T$ and  $0\le U^{j,m}_{p}\le 1,$ 
% % \begin{align*}
% $0\le c_{i+1/2}^{j,k,n}=\Delta x \D t \sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i+1/2-p} U^{j,m}_{p}\le \Delta x \D t \sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i+1/2-p}
% \leq 1,$
% % \end{align*}
% proving \eqref{eq:c1}.
% Now, using Lemma \ref{Pos}, we have
 % Using repeated use of Mean value theorem on ${\mu}^{j,k}$ and ${\dot{\mu}}^{j,k},$ we have, 
% \begin{align*}
%     \begin{split}
%     &\abs{( c^{j,k,n}_{i+3/2} - c^{j,k,n}_{i+1/2}) -( c^{j,k,n}_{i+1/2} - c^{j,k,n}_{i-1/2}) }
%     % = 
%     % \Delta x \D t \bigg|\Delta_x^+\left(\sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i+1/2-p} U^{j,m}_{p}\right)-\Delta_x^+\left(\sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i-1/2-p} U^{j,m}_{p}\right) \bigg|\\
%     % %  &\le 
%     % \Delta x \D t \sum\limits_{k=0}^n\bigg|\sum\limits_{p\in\Z} U^{j,m}_{p}\Theta^{j,k,n-m}_{i-p-1} -2\sum\limits_{p\in\Z} U^{j,m}_{p}\Theta^{j,k,n-m}_{i-p}+\sum\limits_{p\in\Z} U^{j,m}_{p}\Theta^{j,k,n-m}_{i-p+1} \bigg|\\
%       \le 
%     \Delta x \D t \sum\limits_{m=0}^n\sum\limits_{p\in\Z}U^{j,m}_{p}\bigg|\Delta_x^+\Theta^{j,k,n-m}_{i+1/2-p}-\Delta_x^+\Theta^{j,k,n-m}_{i-1/2-p}\bigg|= \mathcal{C}_6^k (\D x)^2 ,
%     \end{split}
% \end{align*}
% where $C_6:=2\norma{U_{0}^k}_{L^1(\R)} {\norma{\ddot{\mu}^{j,k}}_{L^{\infty}(\R)}} \norma{\Gamma^{j,k}}_{L^1(\R^+)}.$  This completes the proof of 
% proving \eqref{eq:c3}. 
% We detail the proof of \eqref{cd2}. 
% Let \[\Gamma^{j,k,r}=\int_{C^r}\Gamma^{j,k}(\tau)\d \tau, G^{j,k,q} := \int_0^{t^{q+1}} \Gamma^{j,k}(\tau)\, d\tau= \sum\limits_{r=0}^q \, \Gamma^{j,k,r}, q\ge0.\] Then, since $\Gamma^{j,k,r} \ge 0,$
% $G^{j,k,q+1} - G^{j,k,q}
% = \, \Gamma^{j,k,q+1}\ge 0,$  and 
% $
% 0 \le G^{j,k,q}
% \le \displaystyle\int_0^\infty \Gamma^{j,k}(t)\, dt
% = 1.$
%  Note that
% \[
% \sum\limits_{m\in\mathcal{N}_T} m\Delta t\,\Gamma^{j,k,m}
% = \sum\limits_{m\in\mathcal{N}_T}m\Delta t\int_{C^m}\Gamma^{j,k}(\tau)\,d\tau .
% \]
% For every $\tau\in C^m,$ we have $t_m\le \tau$.
% Using the nonnegativity of $\Gamma^{j,k}$, this implies
% \[
% m\Delta t\,\Gamma^{j,k}(\tau)
% \le \tau\,\Gamma^{j,k}(\tau).
% \]

% Therefore,
% \begin{align*}
% \sum\limits_{m\in\mathcal{N}_T} m\Delta t\,\Gamma^{j,k,m}
% &\le 
% \sum\limits_{m\in\mathcal{N}_T}\int_{C^m}
% \tau\,\Gamma^{j,k}(\tau)\,d\tau= \int_{0}^{\infty}
% \tau\,\Gamma^{j,k}(\tau)\,d\tau
% \end{align*}
% Using \ref{Moment}, we have,
% \[
% \sum\limits_{m\in\mathcal{N}_T} m\Delta t\,\Gamma^{j,k,m}
%  \le C_{\boldsymbol{\Gamma}}.\]
% Further, 
% \begin{align*}
% c_{i+1/2}^{j,k,n}
% &= \Delta x \sum\limits_{m=0}^n \, \Gamma^{j,k,n-m}
%    \sum\limits_p \mu^{j,k}_{i+1/2-p}\, U^{j,m}_{p} \\
% &= \Delta x \sum\limits_{m=0}^{n-1}
%    \bigl( G^{j,k,n-m} - G^{j,k,n-m-1} \bigr)
%    \sum\limits_p \mu^{j,k}_{i+1/2-p}\, U^{j,m}_{p}+\Delta x 
%    \Gamma^{j,k,0}
%    \sum\limits_p \mu^{j,k}_{i+1/2-p}\, U^{j,n}_{p}\\
% &= \Delta x \sum\limits_{m=1}^n G^{j,k,n-m}
%    \sum\limits_p \mu^{j,k}_{i+1/2-p}
%    \bigl( U^{j,m}_{p} - U^{j,m-1}_{p} \bigr) +\Delta x 
%    \Gamma^{j,k,0}
%    \sum\limits_p \mu^{j,k}_{i+1/2-p}\, U^{j,n}_{p} 
% \end{align*}
% and
% \begin{align*}
% c_{i-1/2}^{j,k,n}
% &= \Delta x \sum\limits_{m=1}^n G^{j,k,n-m}
%    \sum\limits_p \mu^{j,k}_{i-1/2-p}
%    \bigl( U^{j,m}_{p} - U^{j,m-1}_{p} \bigr) +\Delta x 
%    \Gamma^{j,k,0}
%    \sum\limits_p \mu^{j,k}_{i-1/2-p}\, U^{j,n}_{p} 
% \end{align*}
% Thus,
% \[
% c_{i+1/2}^{j,k,n} - c_{i-1/2}^{j,k,n}
% = \Delta x \sum\limits_{m=1}^n G^{j,k,n-m}
%   \sum\limits_p \bigl( \mu^{j,k}_{i+1/2-p} - \mu^{j,k}_{i-1/2-p} \bigr)
%   \bigl( U^{j,m}_{p} - U^{j,m-1}_{p} \bigr) +\Delta x 
%    \Gamma^{j,k,0}
%    \sum\limits_p \bigl( \mu^{j,k}_{i+1/2-p} - \mu^{j,k}_{i-1/2-p} \bigr)\, U^{j,n}_{p}.
% \]
% and 
% \[
% c_{i+1/2}^{j,k,n-1} - c_{i-1/2}^{j,k,n-1}
% = \Delta x \sum\limits_{m=1}^{n-1} G^{j,k,n-1-m}
%   \sum\limits_p \bigl( \mu^{j,k}_{i+1/2-p} - \mu^{j,k}_{i-1/2-p} \bigr)
%   \bigl( U^{j,m}_{p} - U^{j,m-1}_{p} \bigr) +\Delta x 
%    \Gamma^{j,k,0}
%    \sum\limits_p \bigl( \mu^{j,k}_{i+1/2-p} - \mu^{j,k}_{i-1/2-p} \bigr)\, U^{j,n-1}_{p}.
% \]
% Therefore,
% \begin{align*}
% &\sum\limits_i \Big|
% \bigl( c^{j,k,n}_{i+1/2} - c^{j,k,n}_{i-1/2} \bigr)
% - \bigl( c^{j,k,n-1}_{i+1/2} - c^{j,k,n-1}_{i-1/2} \bigr)
% \Big| \\
% &\quad \le
% \Delta x \sum\limits_{m=0}^{n-1}
% \bigl( G^{j,k,n-m} - G^{j,k,n-1-m} \bigr)
% \sum\limits_{i,p}
% \bigl| \mu^{j,k}_{i+1/2-p} - \mu^{j,k}_{i-1/2-p} \bigr|
% \, \bigl| \Delta U^{j,m}_{p} \bigr| \\
% &\quad \le
% \mathcal{C}_9^k\, \Delta t \, \| \mu^{j,k} \|_{BV(\mathbb{R})},\end{align*}
% using Lemma \ref{lem:L1t}.
    \begin{proof}We skip here; the proofs of \ref{lem:monotone}-\ref{lem:entropy} and \ref{eq:c_i+1/2}(\ref{eq:c1}) are quite classic by now in the literature of nonlocal conservation laws; see, for example, \cite{ACT2015, AHV2023, AV2023,ACG2015} and references therein. {\color{black}Items~\ref{lem:BV} and \eqref{eq:c2}-\eqref{eq:c3} are crucial and would yield spatial bounds that depend solely on $\|\Gamma^{j,k}\|_{L^1(\mathbb{R})}$ and are independent of $\|\Gamma^{j,k}\|_{L^{\infty}(\mathbb{R})}$. This property would enable the asymptotic passage from the memory-to-memoryless limit in \S\ref{NLL}. Therefore, in what follows, we prove these estimates one by one.} Note that \begin{align*}
\abs{c^{j,k,n}_{i+1/2} - c^{j,k,n}_{i-1/2}}
&= \Delta x \D t \bigg|\Delta_x^+\left(\sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i-1/2-p} U^{j,m}_{p}\right)\bigg|\\&= \Delta x\Delta t\sum\limits_{m=0}^n\sum\limits_{p\in\mathbb Z}
\bigg|\Delta_x^+\left(\mu^{j,k}_{i-1/2-p}\right)\bigg||\Gamma^{j,k}(t^{n-m})|U^{j,m}_p \\
&\le \Delta t\sum\limits_{m=0}^n|\Gamma^{j,k}(t^{n-m})|\Delta x\sum\limits_{p\in\mathbb Z}U^{j,m}_p\int_{C_{i-p}} |\dot{\mu}^{j,k}(s)|\,ds\le \mathcal{C}_5^k \D x,\end{align*} 
where
$\mathcal{C}_5^k:=\norma{U_{0}^k}_{L^1(\R)}\norma{\dot{\mu}^{j,k}}_{L^\infty(\R)}\norma{\Gamma^{j,k}}_{L^1(\R^+)},$
proving \eqref{eq:c2}. By a  repeated use of the mean value theorem on ${\mu}^{j,k}$ and ${\dot{\mu}}^{j,k},$ we have, 
\begin{align*}
    \begin{split}
    &\abs{( c^{j,k,n}_{i+3/2} - c^{j,k,n}_{i+1/2}) -( c^{j,k,n}_{i+1/2} - c^{j,k,n}_{i-1/2}) }
    \\&= 
    \Delta x \D t \bigg|\Delta_x^+\left(\sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i+1/2-p} U^{j,m}_{p}\right)-\Delta_x^+\left(\sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i-1/2-p} U^{j,m}_{p}\right) \bigg|\\
    &\le 
     \Delta x \D t \sum\limits_{k=0}^n\bigg|\sum\limits_{p\in\Z} U^{j,m}_{p}\Theta^{j,k,n-m}_{i-p-1} -2\sum\limits_{p\in\Z} U^{j,m}_{p}\Theta^{j,k,n-m}_{i-p}+\sum\limits_{p\in\Z} U^{j,m}_{p}\Theta^{j,k,n-m}_{i-p+1} \bigg|\\
      & \le 
    \Delta x \D t \sum\limits_{m=0}^n\sum\limits_{p\in\Z}U^{j,m}_{p}\bigg|\Delta_x^+\Theta^{j,k,n-m}_{i+1/2-p}-\Delta_x^+\Theta^{j,k,n-m}_{i-1/2-p}\bigg|= \mathcal{C}_6^k (\D x)^2 ,
    \end{split}
\end{align*}
where $C_6:=2\norma{U_{0}^k}_{L^1(\R)} {\norma{\ddot{\mu}^{j,k}}_{L^{\infty}(\R)}} \norma{\Gamma^{j,k}}_{L^1(\R^+)}.$  This completes the proof of \eqref{eq:c3}. To prove \ref{lem:BV}, we use the incremental form of \eqref{scheme2}, 
       the CFL condition \eqref{CFL_LF}, and repeating the Harten's argument (see \cite[Lem.~3.12]{HR2015}), we have 
   \begin{align}
\nonumber     U_{i+1}^{k,n+1}-U_{i}^{k,n+1}
% \label{ABC}
&:=\mathcal{A}^{k,n}_{i,1}+\mathcal{A}^{k,n}_{i,2}+\mathcal{A}^{k,n}_{i,3},\end{align}
      where
        \begin{align*}
&\mathcal{A}^{k,n}_{i,1}=(U_{i+1}^{k,n}-U_{i}^{k,n}) \left(1-
      a^{k,n}_{i+1/2}-
      b^{k,n}_{i+1/2}\right)+
      a^{k,n}_{i-1/2}(U_{i}^{k,n}-U_{i-1}^{k,n}) +
      b^{k,n}_{i+1/2}(U_{i+2}^{k,n}-U_{i+1}^{k,n})
     % ÷\ \label{1},
      \\
     & \mathcal{A}^{k,n}_{i,2}=-\lambda \left(
        {\color{black}\mathcal{F}^{k,n}_{{i+3/2}} (U_{i+1}^{k,n},U_{i+1}^{k,n})}
        -
          {\color{black}\mathcal{F}^{k,n}_{{i+1/2}}(U_{i+1}^{k,n},U_{i+1}^{k,n})}
\right),\\
&\mathcal{A}^{k,n}_{i,3}=\lambda\left({\color{black}\mathcal{F}^{k,n}_{{i+1/2}} (U_{i}^{k,n},U_{i}^{k,n})}
        -
          {\color{black}\mathcal{F}^{k,n}_{{i-1/2}} (U_{i}^{k,n},U_{i}^{k,n})}
      \right),\\
      & a^{k,n}_{i-1/2}
     = 
    \lambda \,
    \frac{ {\color{black}\mathcal{F}^{k,n}_{{i-1/2}} (U_{i}^{k,n},U_{i}^{k,n})}
      - \mathcal{F}^{k,n}_{{i-1/2}} (U_{i-1}^{k,n},U_{i}^{k,n})}{(U_{i}^{k,n}-U_{i-1}^{k,n})},
      % \le \frac{1}{3}\,,\\
    \\& b^{k,n}_{i+1/2}
     = 
    \lambda \,
    \frac{
{\color{black}\mathcal{F}^{k,n}_{{i+1/2}} (U_{i}^{k,n},U_{i+1}^{k,n})}
      -
      \mathcal{F}^{k,n}_{{i+1/2}} (U_{i}^{k,n},U_{i}^{k,n})}{(U_{i+1}^{k,n}-U_{i}^{k,n})}.
      % \\
      % \end{split}
   % \end{align*} 
   \end{align*}
With similar calculations as in  \cite{ACT2015} and using \eqref{CFL_LF}, we have $0\le  a^{k,n}_{i+1/2},  b^{k,n}_{i+1/2}\le 1/3,$ implying
% we have, 
 % {\color{black}{mention the CFL}}
% \begin{align*}
    % \begin{equation}\label{A}     
$$\sum\limits_{i\in\Z}\modulo{\mathcal{A}^{k,n}_{i,1}}\ge\sum\limits_{i\in\Z}\modulo{U_{i+1}^{k,n}-U_{i}^{k,n}}.$$
   {Further,}
\begin{align*}\begin{split}\frac{\mathcal{A}^{k,n}_{i,2}+\mathcal{A}^{k,n}_{i,3}}{\lambda}
       &= 
      - \left((f^k(U^{k,n}_{i+1})-f^k(U^{k,n}_{i})\right)
        \left( (\nu^k(\boldsymbol{c}^{k,n}_{{i+3/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}})\right)\\
     &\quad -  f^k(U^{k,n}_{i})\left((\nu^k(\boldsymbol{c}^{k,n}_{{i+3/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}))-(
         \nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}))
      \right).
      \end{split}
    \end{align*}
Using the facts that {$f^k(0)=0$ and $0\le U_i^{k,n}\le 1,$} we have,
    %  \begin{enumerate}
    %  \item 
    % \begin{align*}
   $$|f^k(U^{k,n}_{i})|
    \leq 2\abs{f^k}_{\lip(\\R)} U_i^{k,n}\le 2\abs{f^k}_{\lip(\\R)}.$$
 % \end{align*}
 Finally, using the above estimate in addition to Lemma~\ref{eq:c_i+1/2} and {mean value theorem on $\nu^k$ and $\nabla{\nu}^k$}, we have
\begin{align*}
& |{\mathcal{A}^{k,n}_{i,2}+\mathcal{A}^{k,n}_{i,3}}|
  \\&\le\lambda \modulo{f^k(U^{k,n}_{i+1})-f^k(U^{k,n}_{i})}
  \norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}\modulo{\boldsymbol{c}^{k,n}_{i+3/2}-\boldsymbol{c}^{k,n}_{i+1/2}} \\&\quad+
      \lambda \abs{f^k}_{\lip(\R)}\norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}\abs{U_i^{k,n}}\modulo{\boldsymbol{c}^{k,n}_{i+3/2}-2\boldsymbol{c}^{k,n}_{i+1/2}+\boldsymbol{c}^{k,n}_{i+1/2}}\\
         &{\quad+  \lambda \abs{f^k}_{\lip(\R)}\abs{{{\color{black}\nabla }}{\nu^k}}_{(\lip(\R^N))^{N}}\modulo{\boldsymbol{c}^{k,n}_{i+1/2}-\boldsymbol{c}^{k,n}_{i-1/2}}\abs{U_i^{k,n}}\left(\modulo{\boldsymbol{c}^{k,n}_{i+1/2}-\boldsymbol{c}^{k,n}_{i-1/2}}+\modulo{\boldsymbol{c}^{k,n}_{i+3/2}-\boldsymbol{c}^{k,n}_{i+1/2}}\right)}
        \\
         &\le\Delta t\abs{{\color{black}\nabla }{\nu^k}}_{(\lip(\R^N))^{N}}\abs{f^k}_{\lip(\R)}\modulo{U_{i}^{k,n}-U_{i}^{k,n}}\mathcal{C}_5^k \\&\quad +
    \abs{f^k}_{\lip(\R)}\norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}} \abs{U_i^{k,n}}\mathcal{C}_6^k\Delta x\Delta t\\
         &\quad+  2\abs{f^k}_{\lip(\R)}\abs{{{\color{black}\nabla }}{\nu^k}}_{(\lip(\R^N))^{N}}\abs{U_i^{k,n}}(\mathcal{C}^k_5)^2\Delta x\Delta t.  \end{align*}
Now, summing up  $|{\mathcal{A}^{k,n}_{i,2}+\mathcal{A}^{k,n}_{i,3}}|$ over all $i$,
        \begin{align}
   \nonumber \sum\limits_{i\in\Z} |{\mathcal{A}^{k,n}_{i,2}+\mathcal{A}^{k,n}_{i,3}}|&\le \mathcal{C}_5^k\Delta t  \abs{f^k}_{\lip(\R)}  { \norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}}\sum\limits_{i\in\Z}\abs{U_{i+1}^{k,n}-U_{i}^{k,n}}\nonumber\\&\nonumber\quad+ \mathcal{C}_6^k\Delta t \abs{f^k}_{\lip(\R)}\norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}\norma{U_{0}^k}_{L^1(\R)} \\ \nonumber
      &\quad+2(\mathcal{C}^k_5)^2\Delta t\abs{f^k}_{\lip(\R)}\abs{{{\color{black}\nabla }}{\nu^k}}_{(\lip(\R^N))^{N}}\norma{U_{0}^k}_{L^1(\R)}\\  \label{BC}  
       &=\mathcal{C}_7^k\Delta t \sum\limits_{i\in\Z}\abs{U_{i+1}^{k,n}-U_{i}^{k,n}} 
       + \mathcal{C}_8^k\Delta t,
       \end{align}
       finishing the proof.
%       where  \begin{align*}
% \mathcal{C}_7^k&=\mathcal{C}_5^k \abs{f^k}_{\lip(\R)}  { \norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}},\\
% \mathcal{C}_8^k&=\mathcal{C}_6^k\abs{f^k}_{\lip(\R)}\norma{{\color{black}\nabla }{\nu^k}}_{(L^{\infty}(\R^N))^{N}}
% {+2(\mathcal{C}^k_5)^2\abs{f^k}_{\lip(\R)}\norma{{\color{black}\nabla }{\nu^k}}_{(\lip(\R^N))^{N}}}.
%       \end{align*}
%         { \color{black}Combining the estimates \eqref{ABC}, \eqref{A}-\eqref{BC}, we get the required result. Consider,
%   \begin{align*}
%   &\sum \limits_{i\in \Z}\abs{\Delta^+_t(U_i^{k,n})} \\
%   &\leq \lambda  \sum \limits_{i\in \Z} \abs{\Delta^+_{x}(\mathcal{F}^k(\nu^k(c_{i-1/2}^{j,k,n} ),U_{i-1}^n,U_{i}^n))} \\
%   & \leq \lambda \abs{\mathcal{F}}_{\lip([0,1]^3)} \sum\limits_{i \in \Z} (\abs{\Delta^+_{x}(\nu^k(c_{i-1/2}^{j,k,n} )} + \abs{\Delta^+_{x}(U_{i-1}^n)}+ \abs{\Delta^+_x(U_{i}^n)}.
%   % \\
%   % &\leq  \lambda  \sum \limits_{i\in \Z}\abs{\mathcal{F}^k(\nu^k(c_{i+1/2}^{j,k,n} ),U_{i}^{k,n},U_{i+1}^n)-\mathcal{F}^k(\nu^k(c_{i-1/2}^{j,k,n} ),U_{i}^{k,n},U_{i+1}^n)}\\
%   %  & \quad + \lambda  \sum \limits_{i\in \Z}\abs{\mathcal{F}^k(\nu^k(c_{i-1/2}^{j,k,n} ),U_{i}^{k,n},U_{i+1}^n)
%   %  -\mathcal{F}^k(\nu^k(c_{i-1/2}^{j,k,n} ),U_{i-1}^n,U_{i}^n)}\\
%   %  & \leq 
%   \end{align*}
%   % For a fixed $c_{i+1/2}^{j,k,n} $, since $\mathcal{F}_{i+1/2}^n$ is Lispchitz in each of its variables, we have 
%   % \begin{align*} &\sum \limits_{i\in \Z}\abs{U_i^{k,n+1}-U_{i}^{k,n}} \\ 
%   % & \leq  \sum \limits_{i\in \Z} \abs{\nu^k(c_{i+1/2}^{j,k,n} )} \abs{F(U_{i}^{k,n},U_{i+1}^n)-F(U_{i-1}^n,U_{i}^n)} \\&\quad + \sum \limits_{i\in \Z} \abs{\nu^k(c_{i+1/2}^{j,k,n} )-\nu^k(c_{i-1/2}^{j,k,n} )} \abs{F(U_{i-1}^n,U_{i}^n)}
%   % \end{align*}
%   % {{add the details as time is involved in the convolution}}
% % Further, from \eqref{TVC},
% % \begin{align*}
% % \begin{split}
% % \sum\limits_{i\in\Z}\abs{\Delta^+_{x}(c_{i-1/2}^{j,k,n} )}&= \Delta x \D t \sum\limits_{i\in\Z}\bigg|\Delta^+_{x}\bigg(\sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i-1/2-p} U^{j,m}_{p}\bigg)\bigg|\\
% % &=\Delta x \D t \sum\limits_{m=0}^n\sum\limits_{p\in\Z} U^{j,m}_{p}\sum\limits_{i\in\Z}\bigg|\Delta^+_{x}\bigg(\Theta^{j,k,n-m}_{i-1/2-p}\bigg)\bigg|\\
% % &\le \Delta x \norma{U^{k,\Delta}(t^k,\dott)}_{L^1(\R)}\abs{\mu^{j,k}}_{\operatorname{BV}(\R)}\norma{\Gamma^{j,k}}_{L^1(\R^+)} \\
% % &= \Delta x \norma{U_{0}^k}_{L^1(\R)}\abs{\mu^{j,k}}_{\operatorname{BV}(\R)}\norma{\Gamma^{j,k}}_{L^1(\R^+)}.
% % \end{split}
% % \end{align*}
%   Now using Lem.~\ref{eq:c2}, the total variation bounds on $u^n$ and $\nu^k(c^{j,k,n})$ (cf. Lemma~ \ref{lem:BV}), we have
%   \begin{align*}
%   \D x \sum \limits_{i\in \Z}\abs{\Delta^+_tu_i^{k,n}} \leq \D t \abs{\mathcal{F}}_{\lip([0,1]^3)}  (2\TV(U^{k,n})+\TV(\nu^k(c^{j,k,n}))):= \mathcal{C}_9^k\D t,
%   \end{align*}
%   which implies the desired time estimate.}
%         \begin{align*}
%  \sum\limits_{i\in\Z}\abs{\Delta_x^+(U_{i}^{n+1})}&\le  \sum\limits_{i\in\Z}\abs{U_{i+1}^{k,n}-U_{i}^{k,n}}   (1+\mathcal{C}_7^k\Delta t  )  
%      + \mathcal{C}_8^k\Delta t\nonumber\\
%      % &\le  (\sum\limits_{i\in\Z}\abs{\Delta_x^+(u_i^{n-1})}   (1+\mathcal{C}_7^k\Delta t  )  
%      % + \mathcal{C}_8^k\Delta t)(1+\mathcal{C}_7^k\Delta t  )  +\mathcal{C}_8^k\Delta t\\
%      % &=\sum\limits_{i\in\Z}\abs{\Delta_x^+(u_i^{n-1})}   \left((1+\mathcal{C}_7^k\Delta t  )^2  
%      % + \mathcal{C}_8^k\Delta t(1+\mathcal{C}_7^k\Delta t  ) \right) +\mathcal{C}_8^k\Delta t  \qquad Remove\\
% % &\leq\sum\limits_{i\in\Z}\abs{\Delta_x^+(u_i^{n-1})}   (1+\mathcal{C}_7^k\Delta t  )^2  
% %      + \mathcal{C}_8^k\Delta t\left(1+(1+\mathcal{C}_7^k\Delta t  ) \right) 
% %      \\&\le (\sum\limits_{i\in\Z}\abs{\Delta_x^+(u_i^{n-2})}   (1+\mathcal{C}_7^k\Delta t  )  
% %      + \mathcal{C}_8^k\Delta t)  (1+\mathcal{C}_7^k\Delta t  )^2  
% %      + \mathcal{C}_8^k\Delta t\left(1+(1+\mathcal{C}_7^k\Delta t  ) \right) 
% % % \\&=\sum\limits_{i\in\Z}\abs{\Delta_x^+(u_i^{n-2})}   (1+\mathcal{C}_7^k\Delta t  )^3   
% % %      + \mathcal{C}_8^k\Delta t\left(1+(1+\mathcal{C}_7^k\Delta t  ) +(  (1+\mathcal{C}_7^k\Delta t  )^2 \right) 
% % \\&=\sum\limits_{i\in\Z}\abs{\Delta_x^+(u_i^{n-2})}   (1+\mathcal{C}_7^k\Delta t  )^3   
% %      + \mathcal{C}_8^k\Delta t\sum\limits_{k=0}^{2}\left(1+\mathcal{C}_7^k\Delta t\right)^k.
% %         \end{align*}}
% %            {Proceeding like this, we have,
% %         \begin{align}\nonumber
% %     \sum\limits_{i\in\Z}\abs{\Delta_x^+(U_{i}^{k,n})}&\le  \sum\limits_{i\in\Z}\abs{\Delta_x^+(u_i^{0})}   (1+\mathcal{C}_7^k\Delta t  )^{k,n} 
% %      + \mathcal{C}_8^k\Delta t\sum\limits_{k=0}^{k,n}\left(1+\mathcal{C}_7^k\Delta t\right)^k\\ \nonumber 
% %      &\le \sum\limits_{i\in\Z}\abs{\Delta_x^+(u_i^{0})}(1+\mathcal{C}_7^k\Delta t)^{k,n}
% %      + \mathcal{C}_8^k\Delta t\frac{1-(1+\mathcal{C}_7^k\Delta t)^{k,n}}{1-(1+\mathcal{C}_7^k\Delta t)}\\ \nonumber 
% %      &= \sum\limits_{i\in\Z}\abs{\Delta_x^+(u_i^{0})}(1+\mathcal{C}_7^k\Delta t  )^{k,n}
% %      + \frac{\mathcal{C}_8^k}{\mathcal{C}_7^k}((1+\mathcal{C}_7^k\Delta t)^{k,n}-1)\\ \label{bv:su}
%      &\le \sum\limits_{i\in\Z}\abs{\Delta_x^+(u_i^{0})}\exp(\mathcal{C}_7^k t^n)
%      + \frac{\mathcal{C}_8^k}{\mathcal{C}_7^k}(\exp(\mathcal{C}_7^k t^n)-1),
%         \end{align*}
%  % consequently, we have
%  % \begin{align}\label{bv:u1}
%  %     \sum\limits_{i\in \Z }\abs{U_{i+1}^{k,n+1}-U_{i}^{k,n+1}}\leq  \sum\limits_{i\in \Z } \abs{\Delta_x^+(U_{i}^{k,n})},
%  % \end{align} estav
%  establishing the lemma.
     \end{proof}
% \begin{lemma}[Time estimate]
% \begin{proof}
 
%   \end{proof}
%   \begin{lemma}
%  The scheme \eqref{eq:2} is monotone.
% \end{lemma}
% \begin{proof}
% It is clear the scheme \eqref{final} is monotone and since $U_{i}^{k,n},>0,$ the sch.s monotone.
% \end{proof}
% {To show that the limit of the numerical approximations {$u^{\D}$} are indeed the entropy solutions,} we prove that the approximate solutions {$u^{\D}$} satisfy a discrete
% entropy condition. For this, we introduce the
% following numerical entropy flux,
% ******see~\cite[Proposition~2.8]{ACT2015},
% \cite[Section~3]{CrandallMajda1980},
% \cite[Section~4]{CrandallMajda1980Monotone}:*** references not required **
 
%   & = &
%   g^{k,n}_{{i+1/2}}(u_1 \vee \mathfrak{s}_{\alpha}, u_2 \vee \mathfrak{s}_{\alpha})
%   -
%   g^{k,n}_{{i+1/2}}(u_1 \wedge \mathfrak{s}_{\alpha}, u_2 \wedge \mathfrak{s}_{\alpha}) \,.
% \end{eqnarray*}
% \begin{lemma}
% %  where 
% %  \begin{eqnarray*}
% %  {G^{k,n}_{{i+1/2}}})(U_{i}^{k,n},U_{i+1}^n)(a,b)=\mathcal{F}^{k,n}_{j+1/2} (\beta(a\vee \mathfrak{s}_{\alpha}),\beta(b\vee \mathfrak{s}_{\alpha}))-\mathcal{F}^{k,n}_{j+1/2} (\beta(a\wedge \mathfrak{s}_{\alpha}),\beta(b\wedge \mathfrak{s}_{\alpha})),
% %  \end{eqnarray*}
%  \end{lemma}
% \begin{proof}
% Fix $n\in\mathbb{N}$ and for any sequence $(U^k)_{j\in\Z},$ define the transformation $u\rightarrow H(U^k),$ as
% \begin{eqnarray*}
%  H_j^n(U^k)&=&u_j-\lambda  \bigl[
%     \mathcal{F}^{k,n}_{j+1/2} (\mathfrak{s}_{j}u_j,\mathfrak{s}_{j+1}U_{j+1})  - 
%     \mathcal{F}^{k,n}_{j-1/2} (\mathfrak{s}_{j-1}U_{j-1},\mathfrak{s}_{j}U_{j})
%      \bigr],
% \end{eqnarray*}
% where $\mathcal{F}^{k,n}_{{i+1/2}} (U_{i}^{k,n},U_{i+1}^n)$ is given by \eqref{F}, $\beta_i=\beta(x_i, u_i)$ and but where, instead of \eqref{eq:conv}, the sequence
% $(\boldsymbol{c}^{k,n}_{{i+1/2}})_{i\in\mathbb{Z}}$ is now an arbitrary fixed sequence. Thus, $H_i(U^k)$ depends only on $ U_{i-1}^n, U^{k,n}_i(U^{k,n}_i),$ and $ U_{i+1}^n.$ Then, using \eqref{eq:3}, $H_i^n$ is monotone in ${\mathfrak{s}_{j}u_j}_{\{j=i,i\pm 1\}}$ in the sense that
% \begin{eqnarray*}
%  \frac{\partial H_i^n}{\partial u^n_j}\ge 0, j=i,i\pm 1,
% \end{eqnarray*}
% as in \cite{ACT2015}.
% Since $\beta$ is increasing in $U^k$, consequently, we have 
% \begin{eqnarray*}
%  \frac{\partial H_i^n}{\partial U^{k,n}_j}\ge 0, j=i,i\pm 1.
% \end{eqnarray*}
% For a given $\alpha,$ let $\mathfrak{s}_{\alpha},$ be such that $f^k(\mathfrak{s}_{\alpha})=\alpha.$ Then, we have 
% \[H_i^n(\mathfrak{s}_{\alpha})\vee H_i^n(U^k)\ge H_i^n(U^k\vee \mathfrak{s}_{\alpha}), H_i^n(\mathfrak{s}_{\alpha})\wedge H_i^n(U^k)\le H_i^n(U^k\wedge \mathfrak{s}_{\alpha}). \] Subtracting, we get\begin{eqnarray*}
%  H_i^n(U^k\vee \mathfrak{s}_{\alpha})- H_i^n(U^k\wedge \mathfrak{s}_{\alpha})&\ge& H_i^n(U^k)\vee H_i^n(\mathfrak{s}_{\alpha})- H_i^n(U^k)\wedge H_i^n(\mathfrak{s}_{\alpha})\\
%  &=&\modulo{ H_i^n(U^k)-H_i^n(\mathfrak{s}_{\alpha})}\\
%  &=&\modulo{ U_i^{k,n+1}-H_i^n(\mathfrak{s}_{\alpha})}\\
%   &=&\modulo{U_i^{k,n+1}-\mathfrak{s}_{\alpha}+\lambda f^k(\alpha)(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n}))}\\
%   &=&\sgn(U_i^{k,n+1}-\mathfrak{s}_{\alpha}+\lambda f^k(\alpha)(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n})) )\\
%   &&\times(U_i^{k,n+1}-\mathfrak{s}_{\alpha}+\lambda f^k(\alpha)(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n}))).
% \end{eqnarray*}
% Since the function $(a,b) \rightarrow (\sgn(a+b)-
% \sgn(a))(a+b)$ is always nonnegative, we have 

% \begin{eqnarray*}
%  H_i^n(U^k\vee \mathfrak{s}_{\alpha})- H_i^n(U^k\wedge \mathfrak{s}_{\alpha})&\ge&\sgn(U_i^{k,n+1}-\mathfrak{s}_{\alpha}+\lambda f^k(\alpha)(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n})))\\
%   &&\times(U_i^{k,n+1}-\mathfrak{s}_{\alpha}+\lambda f^k(\alpha)(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n})))\\
%   &\ge &\sgn(U_i^{k,n+1}-\mathfrak{s}_{\alpha})(U_i^{k,n+1}-\mathfrak{s}_{\alpha}+\lambda f^k(\alpha)(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n})))\\
%   &=&\modulo{U_i^{k,n+1}-\mathfrak{s}_{\alpha}}+\lambda\sgn(U_i^{k,n+1}-\mathfrak{s}_{\alpha})\lambda f^k(\alpha)(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n})).
% \end{eqnarray*}

% Also, \begin{eqnarray*}
%  H_i^n(U^k\vee \mathfrak{s}_{\alpha})- H_i^n(U^k\wedge \mathfrak{s}_{\alpha})&=&
%  U_i^{k,n}\vee \mathfrak{s}_{\alpha}-U_i^{k,n}\wedge \mathfrak{s}_{\alpha}-\lambda({G^{k,n}_{{i+1/2}}})(U_{i}^{k,n},U_{i+1}^n)(U_i^{k,n} ,U_{i+1}^{k,n})-
%   G^{k,n}_{{i-1/2}}(U_{i-1}^{k,n} ,U_{i}^{k,n}))\\
%   &=&
%  \modulo{U_i^{k,n}- \mathfrak{s}_{\alpha}}-\lambda({G^{k,n}_{{i+1/2}}})(U_{i}^{k,n},U_{i+1}^n)(U_i^{k,n} ,U_{i+1}^{k,n})-
%   G^{k,n}_{{i-1/2}}(U_{i-1}^{k,n} ,U_{i}^{k,n}))
%  \end{eqnarray*}
%  Finally, we get,
%  \begin{eqnarray*}
% && \modulo{U_i^{k,n}- \mathfrak{s}_{\alpha}}-\lambda\left({G^{k,n}_{{i+1/2}}})(U_{i}^{k,n},U_{i+1}^n)(U_i^{k,n} ,U_{i+1}^{n+1} )-G^{k,n}_{{i-1/2}}(U_{i-1}^{n+1} ,U_i^{k,n+1})\right)\\
%   &&\quad \quad \quad \ge \modulo{U_i^{k,n+1}-\mathfrak{s}_{\alpha}}+\lambda\sgn(U_i^{k,n+1}-\mathfrak{s}_{\alpha})\lambda f^k(\alpha)(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n})),
%  \end{eqnarray*}
% completing the proof.
% \end{proof}
% \begin{proof}
% %  {Let $(i,n)\in \Z\times\mathcal{N}_T$.}
% % Then,
% % \begin{align*}
% % &\abs{U_i^{k,n}-k}-\lambda\left({G^{k,n}_{{i+1/2}}}{(U_{i}^{k,n},U_{i+1}^n)}-G^{k,n}_{{i-1/2}}{(U_{i-1}^n,U_{i}^n)}\right)\\
% % &=H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),\max(U_{i-1}^{k,n},k),\max(U_i^{k,n},k),\max(U_{i+1}^{k,n},k))\\&\quad-H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),\min(U_{i-1}^{k,n},k),\min(U_{i}^{k,n},k),\min(U_{i+1}^{k,n},k))\\
% % &\geq \max(U_i^{k,n+1},H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),k,k,k))\\&\quad-\min(U_i^{k,n+1},H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),k,k,k)
% % \\
% % &=\abs{U_i^{k,n+1}-H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),k,k,k)}\\
% % &=\sgn(U_i^{k,n+1}-H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),k,k,k))\\
% % &\quad \times(U_i^{k,n+1}-H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),k,k,k))\\&
% % = \sgn\left(U_i^{k,n+1}-[k-\lambda f^k(\alpha) (\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}))] \right)  \\& \quad \times \left(U_i^{k,n+1}-[k-\lambda f^k(\alpha) (\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}))] \right)
% % \\
% % &\geq \sgn \left(U_i^{k,n+1}-k \right) \times \left(U_i^{k,n+1}-[k-\lambda f^k(\alpha) (\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}))] \right) \\&= \abs{U_i^{k,n+1}-k} + \lambda f^k(\alpha) \sgn (U_i^{k,n+1}-\alpha)[\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}})].
% % \end{align*} 
% % Here, the first inequality follows from the monotonicity of the scheme Lem. \ref{lem:monotone} and the last inequality follows from the inequality
% % $
% % \sgn(a+b)(a+b) \geq \sgn(a)(a+b).
% % $ This completes the proof. 

% % % \begin{align*}
% &\abs{U_i^{k,n}-k}-\lambda\left({G^{k,n}_{{i+1/2}}}{(U_{i}^{k,n},U_{i+1}^n)}-G^{k,n}_{{i-1/2}}{(U_{i-1}^n,U_{i}^n)}\right)\\
% &=H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),\max(U_{i-1}^{k,n},k,\max(U_i^{k,n},k,\max(U_{i+1}^{k,n},k))\\&\quad-H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),\min(U_{i-1}^{k,n},k),\min(U_{i}^{k,n},k),\min(U_{i+1}^{k,n},k))\\
% % &=(U_i^{k,n} \vee k-U_i^{k,n} \wedgek)\\
% % &\quad-\lambda(\mathcal{F}^{k,n}_{{i+1/2}}\left(\mathfrak{s}(x_i){\max(U_{i}^{k,n}, k)},\,\mathfrak{s}(x_{i+1}){\max(U_{i+1}^n,k)}\right)\\&\quad
% %   -
% %   \mathcal{F}^{k,n}_{{i+1/2}}\left(\mathfrak{s}(x_i){\min(U_{i}^{k,n}, k)},\, \mathfrak{s}(x_{i+1}) {\min(U_{i+1}^n, k)}\right))\\
% %   &\quad+\lambda \mathcal{F}^{k,n}_{{i-1/2}}\left(\mathfrak{s}(x_{i-1}){\max(U_{i-1}^n, k)},\,\mathfrak{s}(x_{i}){\max(U_{i}^n,k)}\right)\\&\quad
% %   -
% %   \mathcal{F}^{k,n}_{{i-1/2}}\left(\mathfrak{s}(x_i){\min(U_{i-1}^n, k)},\, \mathfrak{s}(x_{i}) {\min(U_{i}^n, k)}\right)\\
% %   &=
% %   U_i^{k,n} \vee k\\
% %   &\quad-\lambda\mathcal{F}^{k,n}_{{i+1/2}}\left(\mathfrak{s}(x_i){\max(U_{i}^{k,n}, k)},\,\mathfrak{s}(x_{i+1}){\max(U_{i+1}^n,k)}\right)\\
% % &\quad+\lambda\mathcal{F}^{k,n}_{{i-1/2}}\left(\mathfrak{s}(x_{i-1}){\max(U_{i-1}^n, k)},\,\mathfrak{s}(x_{i}){\max(U_{i}^n,k)}\right)\\&\quad
% %   -
% %   \mathcal{F}^{k,n}_{{i-1/2}}\left(\mathfrak{s}(x_i){\min(U_{i-1}^n, k)},\, \mathfrak{s}(x_{i}) {\min(U_{i}^n, k)}\right)
% % \end{align*}
% % \begin{eqnarray*}
% % &&\abs{U_i^{k,n}-k}-\lambda\left({G^{k,n}_{{i+1/2}}}{(U_{i}^{k,n},U_{i+1}^n)}-G^{k,n}_{{i-1/2}}{(U_{i-1}^n,U_{i}^n)}\right)\\
% % &=
% % H^{k,n}_i(U_i^{k,n} \vee k)-H_i^{k,n}(U_i^{k,n} \wedge k)
% &\geq \max(H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),U_{i-1}^{k,n},U_i^{k,n},U_{i+1}^{k,n}),H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),\mathfrak{s}_{\alpha}(x_{i-1},\mathfrak{s}_{\alpha}(x_{i},k))\\&\quad-\min(H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),U_{i-1}^{k,n},U_i^{k,n},U_{i+1}^{k,n}),H(\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}),\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}}),k,k,k)
% \\&\geq \sgn(U_i^{k,n+1}-H^{k,n}_i(\alpha))  (U_i^{k,n+1}-H^{k,n}_i(\alpha))\\&
% = \sgn\left(U_i^{k,n+1}-[k-\lambda f^k(\alpha) (\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}))] \right)  \\&& \quad \quad \quad \times \left(U_i^{k,n+1}-[k-\lambda f^k(\alpha) (\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}))] \right)
% \\&\geq \sgn \left(U_i^{k,n+1}-k \right) \times \left(U_i^{k,n+1}-[k-\lambda f^k(\alpha) (\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}}))] \right) \\&= \abs{U_i^{k,n+1}-k} + \lambda f^k(\alpha) \sgn (U_i^{k,n+1}-\alpha)[\nu^k(\boldsymbol{c}^{k,n}_{{i+1/2}})-\nu^k(\boldsymbol{c}^{k,n}_{{i-1/2}})]
% % \end{align*} 
% \end{proof}
% \begin{eqnarray}

% -\lambda \left(]
% \mathcal{F}^{k,n}_{{i+1/2}}\left(\beta(x_i,U_i^{k,n}\vee k),\beta(x_{i+1},U_{i+1}^{k,n}\vee k)\right)
% \\&&\quad \quad \quad \quad \quad \quad \quad \quad \quad
% -\mathcal{F}^{k,n}_{{i+1/2}}\left(\beta(x_i,U_i^{k,n}\wedge k),\beta(x_{i+1},U_{i+1}^{k,n}\wedge k)\right)\right)
% \\&&\quad+\lambda \left(
% \mathcal{F}^{k,n}_{{i-1/2}}\left(\beta(x_{i-1},U_{i-1}^{k,n}\vee k),\beta(x_{i},U_{i}^{k,n}\vee k)\right)
% \\&&\quad \quad \quad \quad \quad \quad \quad \quad \quad
% -\mathcal{F}^{k,n}_{{i-1/2}}\left(\beta(x_{i-1},U_{i-1}^{k,n}\wedge k),\beta(x_{i},U_{i}^{k,n}\wedge k)\right)
% \end{eqnarray}






{\begin{theorem}[Convergence]\label{convergence}
Assume that (\textbf{H1})--(\textbf{H3}) hold. As $\Delta x \rightarrow 0$, the approximations $\boldsymbol{U}^{\D}$ 
generated by the  marching formula \eqref{scheme2} converge in $(L^1_{\loc}(\overline{Q}_T))^N$ and pointwise a.e.~in $\overline{Q}_T$ to the entropy solution 
	$\boldsymbol{U}^{\D}\in (L^{\infty}({\overline{Q}_T}))^N \cap (C([0,T];L^1(\R{;[0,1]})))^N$ of the Cauchy problem \eqref{nlm}-\eqref{init}
  with initial data $\boldsymbol{U}_0 \in ((L^1 \cap \operatorname{BV})(\R{;[0,1]}))^N$.
\end{theorem}
\begin{proof}
Lemma \ref{lem:BV} implies that the sequence of functions $\boldsymbol{U}^{\D}(t,\cdot)$ is uniformly total variation bounded. Owing to the time estimate (cf.~Lemma \ref{lem:L1t}) and Helly's theorem (see \cite[Cor.~A.10]{HR2015}) there exists $\boldsymbol{U} \in (L^{\infty}([0,T]; \operatorname{BV}(\R)))^N \cap (C([0,T];L^1(\R{;[0,1]})))^N$ such that up to a subsequence ${\boldsymbol{U}^{\D}} \rightarrow \boldsymbol{U}$ in $(L^1_{\loc}(Q_T))^N.$ 
A Lax-Wendroff type argument presented in  \cite[Thm.~5.1]{BBKT2011} implies that the limit $U^k$ indeed satisfies the entropy condition def.~\eqref{kruz2}. 

% We briefly sketch the proof for the sake of completeness.


% For any non negative test function 
%  $\phi \in C_c^{\infty}(\R),$ define a grid function as $\phi_i^n:=\phi(t^n,x_i).$ Multiplying the discrete entropy inequality \eqref{eq:discrete_entropy} by $\phi_i^n\D x,$ summing over $(i,n)\in \Z\times \mathcal{N}_T$ and finally applying summation by parts, one gets:

% \begin{align*}
%    0&\leq  \D t \sum\limits_{n=0}^N \sum\limits_{i\in \Z} \abs{U_{i}^{k,n}-k} 
%   \frac{\phi_i^{n+1}-\phi_i^n}{\D t }\\
%    &\quad + \D x \D t \sum\limits_{n=0}^N \sum\limits_{i\in \Z} {{G^{k,n}_{{i+1/2}}}(U_i^{k,n} ,U_{i+1}^{k,n})} \frac{\phi_{i+1}^{k,n}-\phi_i^{k,n}}{\D x }\\
%    &\quad - \D x \D t \sum\limits_{n=0}^N \sum\limits_{i\in \Z} \lambda\sgn(U_i^{k,n+1}-\alpha)f^k(\alpha)\frac{(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n}))}{\D x}\phi_i^n\\
%    &\quad + \D x \sum\limits_{i\in \Z} \abs{u_i^0-k} \phi_i^0
%    \\
%    &:=E^{\D}_1+E^{\D}_2+E^{\D}_3+E^{\D}_4.
%    \end{align*}
%    Define 
% \begin{align*}
% \tilde{E}^{\D}_2&:= \D x \D t \sum\limits_{n=0}^N \sum\limits_{i\in \Z} G^{k,n}_{i+1/2}(U_i^{k,n} ,U_{i}^{k,n} ) \frac{\phi_{i+1}^{k,n}-\phi_i^{k,n}}{\D x },\\ 
% \tilde{E}^{\D}_3&:= \D x \D t \sum\limits_{n=0}^N \sum\limits_{i\in \Z} \lambda\sgn(U_i^{k,n}-\alpha)f^k(\alpha)\frac{(\nu^k(\boldsymbol{c}_{i+1/2}^{k,n})-\nu^k(\boldsymbol{c}_{i-1/2}^{k,n}))}{\D x}\phi_i^n.
% \end{align*}
% Using the estimates \eqref{c2}-\eqref{c3}, \begin{align*}
%     \abs{G^n_{i+1/2}(U_{i}^{k,n},U_{i+1}^n)-G^n_{i+1/2}(U_{i}^{k,n},U_{i}^{k,n})} \leq \abs{V^k(\boldsymbol{c}^{k,n}_{i+1/2})} \abs{f^k}_{\lip(\R)}\abs{U_{i+1}^n-U_{i}^n},\end{align*} and following the arguments in \cite[Thm.~5.1]{BBKT2011},
% one obtains\begin{align*}
% \abs{E_2^{\D}-\tilde{E}_2^{\D}} \leq C \D x, \text{ and }
% \abs{E_3^{\D}-\tilde{E}_3^{\D}} \leq C \D x.
% \end{align*}
%    Now, invoking Lebesgue dominated convergence theorem, as $\D x \rightarrow 0$, we have:
%   \begin{align*}
%        E^{\D}_1 &\rightarrow \int_{\Pi_T} \abs{U^k(t,x)-k}\phi_t(t,x) \d t \d x, \\
% \tilde{E}^{\D}_2 &\rightarrow \int_{\Pi_T} \sgn(U^k(t,x)-\alpha)(f^k(U^k(t,x))-f^k(\alpha)) (\nu^k(\Theta*u))(t,x)\phi_x(t,x) \d t \d x,\\
% \tilde{E}^{\D}_3 &\rightarrow \int_{\Pi_T} \sgn(U^k(t,x)-\alpha)f^k(\alpha) \partial_x(\nu^k(\Theta*u))(t,x)\phi(t,x) \d t \d x,\\
%        E^{\D}_4 &\rightarrow \int_{\R} \abs{U_{0}^k(x)-k} \phi(0,x) \d x.
%     \end{align*}

% % Since $\mathfrak{s}\in \operatorname{BV}(\R),$ we have 
% % $\mathfrak{s}_{\alpha}^{\D}:=\frac{\alpha}{\mathfrak{s}^{\D}} \rightarrow \mathfrak{s}_{\alpha}$ in $L^1_{\loc}(\R).$ Consequently the following limits hold:
% % \begin{align*}
% %     E_1 \rightarrow
% %     E_4 \rightarrow
% % \end{align*}

% % The terms $\boldsymbol{c}^{k,n}_{i+1/2}$ satisfy
% Finally, invoking the uniqueness of the entropy solution (see Thm.~ \ref{uniqueness}), in fact, the entire sequence $U^{k,\Delta}$ converges to the entropy solution $U^k$.
% This completes the proof.
\end{proof}

}
% \label{main}
% For $\Delta x, \Delta t>0, $ consider equidistant spatial grid points $x_i:=i\Delta x$ for $i\in\Z$ and temporal grid points $t^n:=n\Delta t$ 
% for integers $0 \le d\le d$,  such that the final time $T \in [t^N, t^{N+1})$. Let $\la:=\D t/\D x$. Let $\chi_{i}(x)$ denote the indicator function of $\mathcal{A}^{k,n}_{i,3}:=[x_i - \D x /2,  x_i + \D x /2)$,  and let
% $\chi^n(t)$ denote the indicator function of $c^{j,k,n}:=[t^n, t^{n+1})$.

% For $\Delta x, \Delta t>0, $ consider equidistant spatial grid points $x_i:=i\Delta x$ for $i\in\Z$ and temporal grid points $t^n:=n\Delta t$ 
% for integers $0 \le d\le d$,  such that the final time $T \in [t^N, t^{N+1})$. Let $\la:=\D t/\D x$. Let $\chi_{i}(x)$ denote the indicator function of $\mathcal{A}^{k,n}_{i,3}:=[x_i - \D x /2,  x_i + \D x /2)$,  and let
% $\chi^n(t)$ denote the indicator function of $c^{j,k,n}:=[t^n, t^{n+1})$.

% We approximate the initial data according to:
% \begin{equation}
% u^0_i=\int_{\mathcal{A}^{k,n}_{i,3}}U_{i}(x)\d{x},  \quad i\in \Z.
% \end{equation}
% % 
% We define a piecewise constant approximate solution ${U^{k,\Delta}}$ to \eqref{introIVP1homos}
% by:
% \begin{equation}
%     {U^{k,\Delta}}(t, x):=\sum\limits_{n=0}^N \sum\limits_{i\in \mathbb{Z}} \displaystyle { \chi_{i}(x)\chi^n (t)} U^{k,n}_i,
% % \end{equation}
% \end{equation}
% In the following section, we prove any two solutions satisfying \eqref{kruz} are unique.
% {
% \begin{corollary}[Regularity of the entropy solution]Assume that (\textbf{A1})--(\textbf{A2}) hold.
% For $0 <t \leq T$ and $U_{0}^k\in (L^1\cap\bv) (\R;[0,1]),$ the the limit $U^k$ of the finite volume approximation  satisfies the following:
% \begin{align*}
% \norma{U^k(t,\dott)}_{L^{\infty}(\R)}&\leq \exp(\mathcal{L}_1T)\norma{U^{k,\Delta}(0)}_{L^{\infty}(\R)}\\
% \norma{U^k(t,\dott)}_{L^1(\R)}&=\norma{U_{0}^k}_{L^1(\R)}\\
% \TV(U^k(t,\dott)) &\leq \exp(\mathcal{L}_2T)(\TV(U_{0}^k) +\mathcal{L}_2)\\
% \norma{U^k(t_2,\dott)-U^k(t_1,\dott)}_{L^1(\R)} &\leq \mathcal{C}_9^k\abs{t_2-t_1}, \text{ where } 0\leq t_1,t_2 \leq T.
% \end{align*}
% \end{corollary}
% }
The above theorems imply that the entropy solution satisfies the following regularity estimates.
% {\color{black}{Do we use it?: yes Lem.~5.4}}
\begin{corollary}[Regularity of the entropy solution]\label{regu}Assume that (\textbf{H1})--(\textbf{H3}) hold.
For $0 <t \leq T$ and $U_{0}^k\in (L^1\cap\bv) (\R;[0,1]),$ the entropy solution $U^k$ of the IVP \eqref{nlm}--\eqref{init} satisfies the following:
\begin{align*}
\norma{U^k(t,\dott)}_{L^{\infty}(\R)}&\leq 1,\\
\norma{U^k(t,\dott)}_{L^1(\R)}&{\color{black}=}\norma{U_{0}^k}_{L^1(\R)},\\ 
\TV(U^k(t,\dott)) &\leq  \left(
     \exp(\mathcal{C}_7^kt)\sum\limits_{i\in\Z}\abs{\TV(U_{0}^k)}  + \frac{\exp(\mathcal{C}_7^kt)-1}{\mathcal{C}_7^k}\mathcal{C}_8^k\right),\\ 
     % \label{TE}
\norma{U^k(t_2,\dott)-U^k(t_1,\dott)}_{L^1(\R)} &\leq \mathcal{C}_9^k\abs{t_2-t_1}, \text{ where } 0\leq t_1,t_2 \leq T.
\end{align*}
\end{corollary}
\begin{remark}\normalfont
  The above discussions in \S\ref{uni} and \S\ref{num} show that entropy solutions of the IVP generate a Lipschitz continuous solution operator $S_t$ on $(\bv(\R))^N$. It is to be noted that the solution operator is not a semigroup in the usual sense because $S_{t+s}(u_0) \neq S_t(S_s(u_0))$. Also, the $\bv$ bounds for $\boldsymbol{U}$ depend solely on $\|\Gamma^{j,k}\|_{L^1(\mathbb{R})}$ and are independent of $\|\Gamma^{j,k}\|_{L^{\infty}(\mathbb{R})}$. In the sequel we invoke this fact to study the memory-to-memoryless Dynamics
\end{remark}
\section{Memory-to-Memoryless Dynamics and Asymptotic Compatibility}\label{NLL}
 In this section, we study the limiting behavior of  the entropy solution of the ``space-time" nonlocal conservation law \eqref{nlm}-\eqref{init} as the kernel $\boldsymbol{\Gamma}$ converges to the Dirac delta distribution. We establish the following results:
\begin{enumerate}[(i)]
\item Theorem~\ref{con} shows that  the entropy solution of \eqref{nlm}--\eqref{init} converges strongly as $\delta \to 0^+$ to the entropy solution of the corresponding ``nonlocal-space'' conservation law \eqref{nls}, with initial data \eqref{init}.
\item Theorem~\ref{rate} shows that the finite volume approximation to \eqref{nlm}--\eqref{init} obtained in \S\ref{num} is asymptotically compatible with the above passage.
\end{enumerate}
This justifies the transition from the model with memory and its numerical approximation to its memoryless counterpart. Moreover, we establish explicit convergence rate estimates that quantify how fast this passage occurs as $\boldsymbol{\Gamma}$ concentrates at the origin. 

 We first introduce some notations and recall a lemma known as the relative entropy estimate for nonlocal conservation laws which is crucial to prove the error estimate. Let $j,k\in\mathcal{N}$ and $T>0$ be the final time. Let $\boldsymbol{\Gamma}$ satisfy \ref{H2A} such that $\Gamma^{j,k}$ has a support in a subset of $ [0,1],$ with $\displaystyle\int_{\R^+}\Gamma^{j,k}(\tau) \d \tau =1$. Further, for any $t>0,$ and for any $\delta>0$, we define,  
 % \begin{equation}\label{thetad}
$\displaystyle\Gamma_{\delta}^{j,k}(t):=\frac{1}{\delta}\Gamma^{j,k}\left(\frac{t}{\delta}\right).$
% \end{equation} 
We define $\Phi: \overline{Q}_T^2 \rightarrow \R$ by  
 % \begin{equation*}
$\Phi(t,x,s,y):=\Phi^{\epsilon,\epsilon_0}(t,x,s,y)=\omega_{\epsilon}(x-y)\omega_{{\epsilon}_0}(t-s),$
% \end{equation*}
where $\omega_a(x)=\displaystyle\frac{1}{a}\omega\left(\frac{x}{a}\right),$ $a>0$ and $\omega$ is a standard symmetric mollifier with $\operatorname{supp} (\omega) \subseteq [-1,1].$ In addition, we assume that $\displaystyle\int_\R \omega_a(x) \d x =1$ and $\displaystyle\int_\R\abs{\omega'_a(x)} \d x =\frac{1}{a}.$ Now, it is straightforward to see that $\Phi$ is symmetric and
$\Phi_x=\omega'_{{\epsilon}}(x-y)\omega_{\epsilon_0}(t-s)=-\Phi_y,  \Phi_t=\omega_{\epsilon}(x-y)\omega'_{{\epsilon}_0}(t-s)=-\Phi_s$.
% \end{enumerate}
For $a,b\in\R, \boldsymbol{Z}, \overline{\boldsymbol{Z}}\in (L^1(Q_T))^N,\phi \in C_c^{\infty}(\overline{Q}_T), \alpha \in \R$ and for $\epsilon,\epsilon_0>0$, let,
 \begin{align*}
% \mathcal{U}_{\mu}^k(t,x)&:=\nu^k((\boldsymbol{\mu}\circledast \boldsymbol{U})^k(t,x)),(t,x)\in \overline{Q}_T,\\
% \mathcal{U}_{\}^k(t,x)&:=\nu^k((\boldsymbol{\mu}\circledast \boldsymbol{U})^k(t,x)),(t,x)\in \overline{Q}_T,\\
 G^k(a,b)&:=\sgn (a-b) (f^k(b)-f^k(a)),\\
% \label{1}
    \Lambda^k_T(Z^k,\phi,\alpha)&:= \int_{Q_T}\Big( |Z^k-\alpha|\phi_{t}+ \nu^k((\boldsymbol{Z}\circledast \boldsymbol{\mu})^k)G(Z^k,\alpha)\phi_{x}
     \\
     & \qquad  \quad  -  \sgn (Z^k-\alpha) f^k(\alpha) \partial_x(\nu^k((\boldsymbol{Z}\circledast \boldsymbol{\mu})^k)\phi\Big) \d t \d x\nonumber \\ & \quad  -\int_{\R}|Z^k(T,x)-\alpha|\phi(T,x)\d x +\int_{\R}|Z^k(0,x)-\alpha|\phi(0,x)\d x, \\
\Lambda^k_{\epsilon,\epsilon_0}(Z^k, \overline{Z}^k)&:=\int_{Q_T}\Lambda^k_T(Z^k,\Phi(\dott,\dott,s,y), \overline{Z}^k(s,y))\d y \d s,
    \\
 \gamma ({Z}^k,\sigma)&:=\sup_{\substack{
    \abs{t_1-t_2} \leq \sigma\\  0\leq t_1< t_2 \leq T }} \norma{{Z}^k(t_1,\dott)-{Z}^k(t_2,\dott)}_{L^1(\R)}.
    % ,\\
    %   \Lambda^k_{\epsilon,\epsilon_0}(v,u)&:=\int_{Q_T}\Lambda_T(v,\Phi(t,x,\dott,\dott), U^k(t,x))\d t \d x.
  \end{align*}
  % {Are $\Lambda^k_{\epsilon,\epsilon_0}(Z^k, \overline{Z}^k)$ and $\Lambda^k_{\epsilon,\epsilon_0}(v,u)$ the same?} 
  % \end{definition}
An estimate on the errors $\norma{\boldsymbol{U}_{\delta}(T)-\boldsymbol{U}(T)}_{(L^1(\R))^N}$ and $\norma{\boldsymbol{U}_{\delta}^{\D}(T)-\boldsymbol{U}(T)}_{(L^1(\R))^N}$ would be achieved by estimating these differences in terms of $\Lambda^k$, which is the relative entropy functional wrt the target conservation law \eqref{nls}. To this end, we recall the relative entropy estimate for  “nonlocal-space” conservation law(see \cite[Lemma~3.3]{AHV2023}):
\begin{lemma}\label{lemma:kuz}[Relative entropy estimate]
% {\color{black}
Let $\boldsymbol{U}$ be the entropy solution  conservation law with memory \eqref{nlm}-\eqref{init} and
let $V$ belong to the set $\mathcal{K} := \Bigl\{ V : Q_T \to \mathbb{R}^N : 
\norma{V}_{(L^\infty(Q_T))^N} + \abs{V}_{(L^\infty_t {\bv}_x)^N} < \infty \Bigr\}.$ Then, the following estimate holds:
\begin{align}\label{kuz1}
\norma{\boldsymbol{U}(T,\dott)-\boldsymbol{V}(T,\dott)}_{(L^1(\R))^N}&\le\mathcal{C}_{10}\left(-\sum\limits_{k\in \mathcal{N}}\Lambda^k_{\epsilon,\epsilon_0}(V^k,U^k)+\sum\limits_{k\in \mathcal{N}}\gamma(V^k,{\epsilon_0})+\epsilon+\epsilon_0 \right), 
\end{align}
  where
  \begin{align*}
\mathcal{C}_{10}=\mathcal{C}_{10}(\boldsymbol{f},\boldsymbol{\mu}, \boldsymbol{\nu}, \norma{\boldsymbol{U}}_{(L^1(Q_T))N},\norma{\boldsymbol{V}}_{(L^1(Q_T))^N},|\boldsymbol{U}|_{(L^\infty_t \operatorname{BV}_x)^N},|\boldsymbol{V}|_{(L^\infty_t \operatorname{BV}_x)^N},|\boldsymbol{U}|_{(L^\infty_t \operatorname{BV}_x)^N},T)
  \end{align*}
and is independent of $\epsilon,\epsilon_0$.
\end{lemma}  Finally, we state and prove the main theorems of this section:
    \begin{theorem}\label{con}
    Let $\boldsymbol{U}$ be the entropy solution of the IVP \eqref{nls},\eqref{init} in the sense of \cite[Def 2.1]{ACG2015}, and let $\boldsymbol{U}_{\delta}$ be the entropy solution of the IVP \eqref{nlm}-\eqref{init} (cf.~Def.~\ref{def:entropy}) with $\Theta^{j,k}=\Theta^{j,k}_{\delta}:=\mu^{j,k}\Gamma^{j,k}_{\delta}$.
    % Under the above hypothesis,
    Then, as $\delta \rightarrow 0,$ $\boldsymbol{U}_{\delta}$  converges to the entropy solution of \eqref{nls},\eqref{init} in $L^1$ norm and satisfies the following error estimate:
\begin{align*}
\norma{\boldsymbol{U}_{\delta}(T)-\boldsymbol{U}(T)}_{(L^1(\R))^N}=\mathcal{O}(\sqrt{\delta}).
\end{align*}
\end{theorem}
% In addition, we show that the numerical approximations generated by the semi-monotone schemes $\boldsymbol{U}^{\Delta}_{\delta}$ are asymptotically compatible with the passage from memory to memoryless limit obtained in Thm.~\ref{con}. More preicelsy we have the following estimate.

% Here, $\boldsymbol{U}_{\delta}$ and $\boldsymbol{U}$ are the entropy solutions of the IVPs \eqref{nlm}-\eqref{init} with $\Theta^{j,k}=\Theta^{j,k}_{\delta}:=\mu^{j,k}\Gamma^{j,k}_{\delta}$ and \eqref{nls},\eqref{init} 
% in the sense of \eqref{kruz2} and \cite[Def 2.1]{ACG2015} respectively, $\boldsymbol{\mu},\boldsymbol{\Gamma}$ satisfy \ref{H2A} and where, for every $j,k\in\mathcal{N}$, $\Gamma^{j,k}$ has a support in a subset of $ [0,1],$ and $\int_{\R^+}\Gamma^{j,k}(\tau) \d \tau =1$. For any $(t,x)\in Q_T,$ and for any $\delta>0$, we define,  \begin{equation}\label{thetad}
%    \Gamma^{j,k}_{\delta}(t):=\frac{1}{\delta}\Gamma^{j,k}\left(\frac{t}{\delta}\right),j,k\in\mathcal{N}.
% \end{equation}


% \end{enumerate}
\begin{proof}
% To prove the Theorem~\ref{con}, we need the following claims:
% \begin{enumerate}[\textbf{Claim \arabic*}:]
    % \item 

    {In view of the relative entropy estimate Lem.~\ref{lemma:kuz}, it is enough to estimate the relative entropy functional $-\Lambda^k_{\epsilon,\epsilon_0}(U^k_{\delta},U^k)$ and modulus of time continuity $\gamma(U_{\delta}^k,\epsilon_0)$.}
    We first prove that, for a fixed ${\delta}>0,$ and for any $\epsilon,\epsilon_0,$
    \begin{align*}
-\Lambda^k_{\epsilon,\epsilon_0}(U^k_{\delta},U^k) \leq \mathcal{C}_{11}^k \left({\delta}/{\epsilon} + {\delta} \right) \qquad \text{for all } k\in \mathcal{N},
\end{align*}
where $\mathcal{C}_{11}^k$ is given by \eqref{C}. Using the entropy inequality \eqref{kruz2} for $U^k_{\delta}$, we have,
\begin{align}\nonumber
&-\Lambda^k_{\epsilon,\epsilon_0}(U^k_{\delta},U^k) \\
 &\nonumber\le \int_{Q_T}\int_{Q_T}G^k(U^k_{\delta}(t,x),U^k(s,y))\nu^k((\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\Theta}}_{\delta})^k)(t,x)) \Phi_x(s,y,t,x) \d t  \d x \d s \d y \\
 &\nonumber\quad - \int_{Q_T}\int_{Q_T}\sgn(U^k_{\delta}(t,x)-U^k(s,y))f^k(U^k(s,y))\partial_x(\nu^k((\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\Theta}}_{\delta})^k)(t,x))) \\
 & \nonumber\qquad  \quad  \qquad \times 
 \Phi(s,y,t,x) \d t  \d x \d s \d y \\
 &\nonumber\quad-\int_{Q_T}\int_{Q_T}G^k(U^k_{\delta}(t,x),U^k(s,y))\nu^k((\boldsymbol{U}_{\delta}\circledast \boldsymbol{\mu})^k)(t,x)\Phi_x(s,y,t,x) \d t  \d x \d s \d y \\
 &\nonumber\quad + \int_{Q_T} \int_{\R}\sgn(U^k_{\delta}(t,x)-U^k(s,y))f^k(U^k(s,y))\partial_x(\nu^k((\boldsymbol{U}_{\delta}\circledast \boldsymbol{\mu})^k)(t,x))\Phi(s,y,t,x) \d t  \d x \d s \d y\\
    % &\quad- \int_{Q_T}\int_{Q_T} \abs(U_{0}^k(x)-U^k(s,y))\Phi(s,y,0,x)  \d x\d s  \d y +\int_{Q_T} \int_{\R} |U^k_{\delta}(T,x)-U^k(s,y)|  \Phi(s,y,T,x)  \d x\d s  \d y.
% \end{align*}
% This implies,
% \begin{align*}
% {\color{red}&\nonumber-\Lambda^k_{\epsilon,\epsilon_0}(U^k_{\delta},U^k) \nonumber} \\
 &\nonumber\le \int_{Q_T}\int_{Q_T} G^k(U^k_{\delta}(t,x),U^k(s,y))(\nu^k((\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\Theta}}_{\delta})^k)(t,x))-\nu^k((\boldsymbol{U}_{\delta}\circledast \boldsymbol{\mu})^k)(t,x)\Phi_x(s,y,t,x) \d t  \d x \d s \d y \nonumber \\
 &\nonumber\quad +\int_{Q_T}\int_{Q_T}\sgn(U^k_{\delta}(t,x)-U^k(s,y))f^k(U^k(s,y)) 
 \nonumber \\&\nonumber
 \qquad \qquad\times(\partial_x(\nu^k((\boldsymbol{U}_{\delta}\circledast \boldsymbol{\mu})^k)(t,x))-\partial_x(\nu^k((\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\Theta}}_{\delta})^k)(t,x)))) \Phi(s,y,t,x) \d t  \d x \d s \d y 
 \nonumber \\ &\nonumber \leq 
 \frac{1}{\epsilon}\abs{f^k}_{\lip(\R)} (\norma{U^k}_{L^{\infty}(Q_T)}+ \norma{U^k_{\delta}}_{L^{\infty}(Q_T)}) \abs{\nu^k}_{\lip(\R)} \int_{Q_T}\norma{(\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\Theta}}_{\delta})^k(t,x)-(\boldsymbol{U}_{\delta}\circledast \boldsymbol{\mu})^k(t,x)} \d x \d t 
 \nonumber \\&\nonumber
 \quad + \abs{f^k}_{\lip(\R)} \norma{U^k}_{L^{\infty}(Q_T)} \int_{Q_T}\norma{\nabla\nu^k((\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\Theta}}_{\delta})^k)(t,x)-\nabla\nu^k((\boldsymbol{U}_{\delta}\circledast \boldsymbol{\mu})^k)(t,x)} \norma{(\boldsymbol{U}_{\delta}\circledast \partial_x\boldsymbol{\mu})^k(t,x)} \d x \d t \nonumber\\
 &\nonumber
 \quad +  \abs{f^k}_{\lip(\R)} \norma{U^k}_{L^{\infty}(Q_T)} \int_{Q_T}  \norma{(\boldsymbol{U}_{\delta}\circledast \partial_x{\boldsymbol{\Theta}}_{\delta})^k(t,x)-(\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\mu}}')^k(t,x)} \norma{\nabla\nu^k(\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\Theta}}_{\delta})^k(t,x)} \d x \d t \nonumber
 \\ & :=\frac{1}{\epsilon}\abs{f^k}_{\lip(\R)} \abs{\nu^k}_{\lip(\R)}(\norma{U^k}_{L^{\infty}(Q_T)}+ \norma{U^k_{\delta}}_{L^{\infty}(Q_T)}) 
 I_1^k \nonumber \\&\quad +\abs{f^k}_{\lip(\R)} \norma{U^k}^2_{L^{\infty}(Q_T)} \norma{\boldsymbol{\mu}'}_{(L^1(\R))^{N^2}}
 \norma{\operatorname{Hess}\nu^k}_{(L^{\infty}(\R^N))^N} I_1^k\nonumber \\
  &\quad+\abs{f^k}_{\lip(\R)} \norma{U^k}_{L^{\infty}(Q_T)}  \norma{\nabla\nu^k}_{(L^{\infty}(\R^N))^N}I_2^k,\nonumber\\& \label{Gamma}
  \end{align}
   \vspace{-7mm}
 \begin{align*}
\text{where }\,I_1^k&:=\int_{Q_T}  \norma{(\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\Theta}}_{\delta})^k(t,x)-(\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\mu}})^k(t,x)} \d x \d t,\\
   I_2^k&:=\int_{Q_T}  \norma{(\boldsymbol{U}_{\delta}\circledast \partial_x{\boldsymbol{\Theta}}_{\delta})^k(t,x)-(\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\mu}}')^k(t,x)} \d x \d t. 
\end{align*}
In what follows, we estimate the  terms $I_1^k$ and $I_2^k$.
Consider 
\begin{align*}
I_1^k&=\int_0^{\delta} \int_{\R}\norma{(\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\Theta}}_{\delta})^k)(t,x)-(\boldsymbol{U}_{\delta}\circledast \boldsymbol{\mu})^k(t,x)} \d x \d t \\& \quad + \int_{\delta} ^T\int_{\R}\norma{(\boldsymbol{U}_{\delta}\circledast {\boldsymbol{\Theta}}_{\delta})^k(t,x)-(\boldsymbol{U}_{\delta}\circledast \boldsymbol{\mu})^k(t,x)} \d x \d t\\
&=\sum\limits_{j=1}^{N}\int_0^{\delta} \int_{\R}\Bigg| \int_0^t\int_{\R}U^j_{\delta}(\tau,\xi)\mu^{j,k}(x-\xi)\Gamma^{j,k}_{\delta}(t-\tau) \d \tau \d \xi  -  \int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi)  \d \xi \Bigg|  \d x \d t \\& \quad + \sum\limits_{j=1}^{N}\int_{\delta} ^T\int_{\R}\Bigg| \int_0^t\int_{\R}U^j_{\delta}(\tau,\xi)\mu^{j,k}(x-\xi)\Gamma^{j,k}_{\delta}(t-\tau) \d \tau \d \xi  -  \int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi)  \d \xi \Bigg|  \d x \d t
% \\
% &=\sum\limits_{j=1}^{N}\int_0^{\delta} \int_{\R}\Bigg| \int_0^t\int_{\R}U^j_{\delta}(\tau,\xi)\mu^{j,k}(x-\xi)\Gamma^{j,k}_{\delta}(t-\tau) \d \tau \d \xi  -  \int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi)  \d \xi \Bigg|  \d x \d t \\& \quad + \sum\limits_{j=1}^{N}\int_{\delta} ^T\int_{\R}\Bigg| \int_{0}^{t}\int_{\R}U^j_{\delta}(\tau,\xi)\mu^{j,k}(x-\xi)\Gamma^{j,k}_{\delta}(t-\tau) \d \tau \d \xi  -  \int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi)  \d \xi \Bigg|  \d x \d t.
\end{align*}
Since $\displaystyle\int_0^{\delta} \Gamma^{j,k}_{\delta}(\tau)\d \tau =1$,   for every $j,k\in\mathcal{N},$ and for every %$(t,x)\in Q_T,$ 
% we have \begin{align*}
% \displaystyle\int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi) \d \xi=\displaystyle\int_0^{\delta}\int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi.\end{align*} 
% Consequently for every $t \in [0,\delta],$  we get,
% \begin{align*}
% &\int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi\\
% % &=\int_0^{t}\int_{\R}U^j_{\delta}(t-\tau,x-\xi)\mu^{j,k}(\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi\\
% % &\qquad-\int_0^{t}\int_{\R}U^j_{\delta}(t,x-\xi)\mu^{j,k}(\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi-\int^{t}_{\delta}\int_{\R}U^j_{\delta}(t,x-\xi)\mu^{j,k}(\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi\\
% &=\int_0^{t}\int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi+\int_{t}^{\delta}\int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi
% \end{align*}
% Consequently for every 
$t\in [\delta,T], x\in \R$ we get,
\begin{align*}
\int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi)  \d \xi \d x &=\int_0^{t}\int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi) \Gamma^{j,k}_{\delta}(t-\tau)\d \tau \d \xi.
\end{align*}
Thus, 
\begin{align*}
I_1^k& 
% \leq \sum\limits_{j\in\mathcal{N}}\int_0^{\delta} \int_{\R} \Bigg( \Bigg| \int_0^t\int_{\R}U^j_{\delta}(\tau,\xi)\mu^{j,k}(x-\xi)\Gamma^{j,k}_{\delta}(t-\tau) \d \tau \d \xi  -  \int_0^{t}\int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi \Bigg| \\
%  & \qquad  \qquad \quad + \Bigg|\int_t^{\delta}\int_{\R}U^j_{\delta}(t,\xi)\mu^{j,k}(x-\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi \Bigg| \Bigg) \d x \d t \\
%  & \quad  + \sum\limits_{j\in\mathcal{N}}\int_{\delta}^T \int_{\R} 
%  \int_0^{t}\int_{\R}
% \abs{U^j_{\delta}(\tau,x-\xi)-U^j_{\delta}(t,x-\xi)}\mu^{j,k}(\xi) \Gamma^{j,k}_{\delta}(t-\tau)\d \tau \d \xi \d x \d t\\
% &\leq \sum\limits_{j\in\mathcal{N}}\int_0^{\delta} \int_{\R} \int_0^t\int_{\R}
% \left| U^j_{\delta}(t-\tau,x-\xi) -U^j_{\delta}(t,x-\xi) \right| \mu^{j,k}(\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi \d x\d t  \\
%  & \quad + \sum\limits_{j\in\mathcal{N}}\int_0^{\delta}\int_{\R}\int_0^t\int_{\R} U^j_{\delta}(t,x-\xi)\mu^{j,k}(\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi  \d x \d t \\
%  & \quad + \sum\limits_{j\in\mathcal{N}}\int_{\delta}^T \int_{\R} 
%  \int_0^{t}\int_{\R}
% \abs{U^j_{\delta}(\tau,x-\xi)-U^j_{\delta}(t,x-\xi)}\mu^{j,k}(\xi) \Gamma^{j,k}_{\delta}(t-\tau)\d \tau \d \xi \d x \d t\\
% &
\leq \sum\limits_{j\in\mathcal{N}}\int_0^{\delta} \int_{\R} \int_0^t\int_{\R}U^j_{\delta}(t-\tau,x-\xi)\mu^{j,k}(\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi \d x\d t\\&\quad+\sum\limits_{j\in\mathcal{N}}\int_0^{\delta} \int_{\R} \int_{\R}U^j_{\delta}(t,x-\xi) \mu^{j,k}(\xi) \d \xi \d x\d t  \\
 % & \quad + \sum\limits_{j\in\mathcal{N}}\int_0^{\delta}\int_{\R}\int_0^t\int_{\R} U^j_{\delta}(t,x-\xi)\mu^{j,k}(\xi) \Gamma^{j,k}_{\delta}(\tau)\d \tau \d \xi  \d x \d t \\
 & \quad + \sum\limits_{j\in\mathcal{N}}\int_{\delta}^T \int_{\R} 
 \int_0^{t}\int_{\R}
\abs{U^j_{\delta}(\tau,x-\xi)-U^j_{\delta}(t,x-\xi)}\mu^{j,k}(\xi) \Gamma^{j,k}_{\delta}(t-\tau)\d \tau \d \xi \d x \d t\\
& \leq 2\delta\norma{\boldsymbol{U}_{0}}_{(L^{1}(\R))^N} \norma{\boldsymbol{\mu}}_{(L^{1}(\R))^{N^2}}   +
{\delta}T\abs{\boldsymbol{U}_{\delta}}_{(\lip_t L^1_x)^N} \norma{\boldsymbol{\mu}}_{(L^{1}(\R))^{N^2}}:=\mathcal{C}_{12}{\delta}.
\end{align*}
\textit{Mutatis mutandis}, we have,
\begin{align*}
%     I_2 &\leq \abs{U^k_{\delta}}_{\lip_t L^1} \norma{\dot{\mu}^{j,k}}_{L^{1}(\R)}  \delta^2 + \norma{U_{0}^k}_{L^{1}(\R)} \norma{\dot{\mu}^{j,k}}_{L^{1}(\R)} \delta + T
% \abs{U^k_{\delta}}_{\lip([0,T];L^1(\R))} \norma{\dot{\mu}^{j,k}}_{L^{1}(\R)} {\delta}\\
I_2^k&\leq 2\delta\norma{\boldsymbol{U}_{0}}_{(L^{1}(\R))^N} \norma{\boldsymbol{\mu'}}_{(L^{1}(\R))^{N^2}}  +
{\delta}T\abs{\boldsymbol{U}_{\delta}}_{(\lip_t L^1_x)^N} \norma{\boldsymbol{\mu}'}_{(L^{1}(\R))^{N^2}}:=\mathcal{C}_{13}{\delta}.
\end{align*}
Substituting the estimates on $I_1^k$ and $I_2^k$ in \eqref{Gamma}, we have,
\begin{align}\label{C}
\begin{split}
-\Lambda^k_{\epsilon,\epsilon_0}(U^k_{\delta},U^k)
&\leq \frac{{\delta}}{\epsilon}\abs{f^k}_{\lip(\R)} \abs{\nu^k}_{\lip(\R)}\left(\norma{U^k}_{L^{\infty}(Q_T)}+ \norma{U^k_{\delta}}_{L^{\infty}(Q_T)}\right) 
\mathcal{C}_{12}\\
&\qquad+{\delta}\abs{f^k}_{\lip(\R)} \norma{U^k}^2_{L^{\infty}(Q_T)} \norma{\boldsymbol{\mu}'}_{(L^1(\R))^{N^2}}
 \norma{\operatorname{Hess}\nu^k}_{(L^{\infty}(\R^N))^N}\mathcal{C}_{12}\\
  &\qquad+{\delta}\mathcal{C}_{13}\abs{f^k}_{\lip(\R)} \norma{U^k}_{L^{\infty}(Q_T)}  \norma{\nabla\nu^k}_{(L^{\infty}(\R^N))^N}:=\mathcal{C}_{11}^k\left(\displaystyle\frac{\delta}{\epsilon}+\delta\right),\end{split}
\end{align}
\vspace{-2mm}
 \begin{align*}
% \begin{split}
   \text{where} \, \, \mathcal{C}_{11}^k&:=\abs{f^k}_{\lip(\R)} \abs{\nu^k}_{\lip(\R)}\left(\norma{U^k}_{L^{\infty}(Q_T)}+ \norma{U^k_{\delta}}_{L^{\infty}(Q_T)}\right) 
\mathcal{C}_{12}\\
&\qquad+\abs{f^k}_{\lip(\R)} \norma{U^k}^2_{L^{\infty}(Q_T)} \norma{\boldsymbol{\mu}'}_{(L^1(\R))^{N^2}}
 \norma{\operatorname{Hess}\nu^k}_{(L^{\infty}(\R^N))^N}\mathcal{C}_{12}\\
  &\qquad+\abs{f^k}_{\lip(\R)} \norma{U^k}_{L^{\infty}(Q_T)}  \norma{\nabla\nu^k}_{(L^{\infty}(\R^N))^N}\mathcal{C}_{13}.
  % \end{split}
\end{align*}
% which proves the claim.
% Finally, we prove Theorem~\ref{con} using the above lemma.\\
% \begin{proofof}{Theorem~\ref{con}}
   Now, since $\boldsymbol{U}_{\delta}$ is the entropy solution of \eqref{nlm}-\eqref{init}, we have
   \begin{align}\label{time}
   \gamma^k(U^k_{\delta},{\delta}) \leq \mathcal{C}_9^k{\delta},
   \end{align} owing to the time estimate (cf.~Cor.~\ref{regu}) with $\mathcal{C}_9^k$ independent of ${\delta}.$
   Finally, using \eqref{C}-\eqref{time} in Lemma~\ref{kuz1} and choosing $\epsilon=\epsilon_0=\sqrt{\delta},$ implies the theorem.
 \end{proof}
% So far we have proved the convergence $u^{\D}_{\delta} \rightarrow U_{\eta}$ and $U_{\eta} \rightarrow u$, consequently the following convergence hold
% \begin{theorem}
% As $(\D , \delta) \rightarrow (0,0)$, $U_{\delta}^{\D} \rightarrow u$ in $L^1(Q_T)$ where $U^k$ is the entropy solution of the conservation law.
% \end{theorem}
% Using \eqref{eq:conv},
% \begin{align*}
% c_{i+1/2}^{j,k,n} & :=\Delta x \D t \sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i+1/2-p} U^{j,m}_{p}  
% \\\nonumber
% &\approx \int_0^{t^n}\int_{\R}\Theta^{j,k}(x_{i+1/2}-\xi,t^n-\tau) U^{j,\D}(\tau,\xi )\d \xi \d \tau, 
% \end{align*}
\begin{theorem}\label{rate}
% Assume that there exists
% $C_{\boldsymbol{\Gamma}}>0$ such that 
% \begin{equation}\label{Moment}
% \displaystyle\int_{\mathbb{R}^{+}} x\,\Gamma^{j,k}(x)\,\d x\le C_{\boldsymbol{\Gamma}} < \infty.
%  \end{equation}
 Let $\boldsymbol{U}$ be the entropy solution of the IVP \eqref{nls},\eqref{init} in the sense of \cite[Def 2.1]{ACG2015}, and let $\boldsymbol{U}^{\Delta}_{\delta}$ be the finite volume approximation to \eqref{nlm}-\eqref{init} obtained in \S\ref{num} with the space-time kernel $\boldsymbol{\Theta}_{\delta}$, where the mollifier $\Gamma$ satisfies \begin{equation}\label{Moment}
\displaystyle\int_{\mathbb{R}^{+}} x\,\Gamma^{j,k}(x)\,\d x \ge C_{\boldsymbol{\Gamma}} > 0.
 \end{equation} for $C_{\boldsymbol{\Gamma}}>0$. Then, as $\Delta x , \delta \rightarrow 0,$ $\boldsymbol{U}^{\Delta}_{\delta}$  converges to the entropy solution $\boldsymbol{U}$ of \eqref{nls},\eqref{init} in $L^1$ norm  and satisfies the following error estimate:
\begin{align*}
\norma{\boldsymbol{U}^{\Delta}_{\delta}(T)-\boldsymbol{U}(T)}_{(L^1(\R))^N} = \mathcal{O}(\sqrt{\delta}+\sqrt{\D x}).
\end{align*} 
\end{theorem}  
\begin{proof}
% We define the necessary notations to estimate the relative entropy functional $\Lambda^k_{\epsilon,\epsilon_0}(U_{\delta}^{k,\D},U^{k})$.
% \begin{align}
% We follow the following notations in this section: \\
   {In view of the relative entropy estimate Lemma~\ref{lemma:kuz}, it is enough to estimate the relative entropy functional $-\Lambda^{k}_{\epsilon,\epsilon_0}(U^{k,\Delta}_{\delta},U^{k})$ and modulus of time continuity $\gamma(U_{\delta}^{k,\Delta},\epsilon_0)$. }
 We first prove that, for a fixed ${\delta}, \Delta x>0,$ and for any $\epsilon,\epsilon_0>0,$ the relative entropy functional satisfies the following estimate:
    \begin{align*}
-\Lambda^k_{\epsilon,\epsilon_0}(U_{\delta}^{k,\D},U^k) \leq \mathcal{C}_{14} \left({\delta}/{\epsilon} + {\delta} \right).
\end{align*}
Let $\sum\limits_{i,n}$ denote the double summation $\sum\limits_{i\in \Z}\sum\limits_{n=0}^{N_T-1}.$ Further, for $\alpha\in \R, \delta>0,i\in \Z, s,n,m\in {\mathcal{N}}_T, j,k \in\mathcal{N}, \alpha\in \R$ and $(t,x)\in Q_T,$ let 
% \begin{align*}
% \item 
$\Gamma^{j,k,s}_{\delta}=\displaystyle\frac{1}{\Delta t}\int_{C^s}\Gamma^{j,k}_{\delta}(\tau)d\tau,
    \eta_{i,\delta}^{k,n}(\alpha):=\abs{U_{i,\delta}^{k,n}-\alpha}$, $p_{i,\delta}^{k,n}(\alpha):=G(U_{i,\delta}^{k,n},\alpha) 
    $ and $c_{i+1/2}^{j,k,n,\delta}  :=\Delta x \Delta t\sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Gamma^{j,k,n-m}_{\delta}\mu^{j,k}_{i+1/2-p} U^{j,m}_{p,\delta}$.
% We first estimate the relative entropy functional $\Lambda^k_{\epsilon,\epsilon_0}(U^{k,\D}_{\delta},U^k).$ 
% \begin{align*}
% &-\Lambda^k_{\epsilon,\epsilon_0}(U^{k,\Delta}_{\delta},U^k) \\
%  &\quad= -\int_{Q_T} \sum\limits_{i,n}   \int_{C_i^n}\eta_{i,\delta}^{k,n}(U^k(s,y))\Phi_t(s,y,t,x) \d t  \d x \d s \d y \\
%  &\qquad-\int_{Q_T} \sum\limits_{i,n}   \int_{C_i^n} p_{i,\delta}^{k,n}(U^k(s,y))\nu^k((\boldsymbol{\mu}\circledast\boldsymbol{U}^{\Delta}_{\delta}(t))^k)(x)\Phi_x(s,y,t,x) \d t  \d x \d s \d y \\
%  &\qquad + \int_{Q_T}\sum\limits_{i,n}  \int_{C_i^n}\sgn(U_{i}^{k,n}-U^k(s,y))f^k(U^k(s,y))\partial_x\nu^k((\boldsymbol{\mu}\circledast\boldsymbol{U}^{\Delta}_{\delta}(t))^k)(x)\Phi(s,y,t,x) \d t  \d x \d s \d y \\
%     &\qquad- \int_{Q_T}\sum\limits_{i}   \int\limits_{C_i}  \eta_{i,\delta}^{k,0}(U^k(s,y)) \Phi(s,y,0,x)  \d x\d s  \d y +\int_{Q_T} \sum\limits_{i}  \int\limits_{C_i}  \eta_{i,\delta}^{k,N_T}(U^k(s,y))  \Phi(s,y,T,x)  \d x\d s  \d y\\
% \end{align*}
Using the fundamental theorem of calculus followed by summation by parts, $-\Lambda^k_{\epsilon,\epsilon_0}(U^{k,\D}_{\delta},U^k)$ can be written as:
\begin{align*}
-\Lambda^k_{\epsilon,\epsilon_0}(U_{\delta}^{k,\D},U^k) &=\lambda_1^k+\lambda_2^k+ \lambda_3^k,\end{align*}
%\vspace{-10mm}
\begin{align*}
\text{where }\lambda_1^k&:=\int_{Q_T} \sum\limits_{i,n} \left(\eta_{i,\delta}^{k,n+1}(U^k(s,y))-\eta_{i,\delta}^{k,n}(U^k(s,y))\right)\int\limits_{C_i}\Phi(s,y,t^{n+1},x)  \d x\d s  \d y, \nonumber\\
 \lambda_2^k&:=-\int_{Q_T} \sum\limits_{i,n} \int_{C_i^n}p_{i,\delta}^{k,n}(U^k(s,y))\nu^k((\boldsymbol{\mu}\circledast\boldsymbol{U}^{\Delta}_{\delta}(t))^k)(x)\Phi_x(s,y,t,x) \d t  \d x \d s \d y, \nonumber\\
 \lambda_3^k&:=\ \int_{Q_T}\sum\limits_{i,n}  \int_{C_i^n}\sgn(U_{i,\delta}^{k,n}-U^k(s,y))f^k(U^k(s,y))\mathcal{U}_x^{k,\Delta}(t,x)\Phi(s,y,t,x) \d t  \d x \d s \d y. \nonumber
\end{align*}
By applying the discrete entropy inequality \ref{lem:entropy} we get:
\begin{align*}
\lambda_1^k&\le
% \int_{Q_T} \sum\limits_{i,n}  \left(\eta_{i,\delta}^{k,n+1}(U^k(s,y))-\eta_{i,\delta}^{k,n}(U^k(s,y))\right)\int\limits_{C_i}\Phi(s,y,t^{n+1},x)  \d x\d s  \d y  \\    \le 
-\lambda \int_{Q_T} \sum\limits_{i,n}  \big(
\mathcal{G}^{k,n}_{i+1/2}(U_i^{k,n} ,U_{i+1}^{k,n},U^k(s,y) )-\mathcal{G}^{k,n}_{i-1/2}(U_{i-1}^{k,n} ,U_i^{k,n},U^k(s,y) )\big)\\&\qquad \qquad  \times \int_{C_i}\Phi(s,y,t^{n+1},x)  \d x\d s  \d y\\
 &\quad -\lambda \int_{Q_T} \sum\limits_{i,n}\sgn(U_i^{k,n+1}-U^k(s,y))f(U^k(s,y) )\left(\nu^k\left(\boldsymbol{c}_{i+1/2}^{k,n,\delta}\right) -\nu^k\left(\boldsymbol{c}_{i-1/2}^{k,n,\delta}\right)\right) \\&\qquad \qquad  \times 
\int_{C_i}\Phi(s,y,t^{n+1},x)  \d x\d s  \d y\\
&:= {\lambda}_{11}^k+{\lambda}_{12}^k.
\end{align*}
 Note that
\begin{align}
    \lambda_2^k&=-\int_{Q_T}\sum\limits_{i,n}  \int_{C_i^n}p_{i,\delta}^{k,n}(U^k(s,y))\nu^k\left(\boldsymbol{c}_{i+1/2}^{k,n,\delta}\right)\Phi_x(s,y,t,x)  \d t\d x\d s  \d y \nonumber\\ 
&\quad-\int_{Q_T}\sum\limits_{i,n}  \int_{C_i^n}p_{i,\delta}^{k,n}(U^k(s,y))\Phi_x(s,y,t,x) \left(\nu^k((\boldsymbol{\mu}\circledast\boldsymbol{U}^{\Delta}_{\delta}(t))^k)(x)-\nu^k\left(\boldsymbol{c}_{i+1/2}^{k,n,\delta}\right)\right)  \d t\d x\d s  \d y \nonumber\\
&:=\overline{\lambda}_2^{k}+\mathcal{E}_2^k, \nonumber\\&  \label{lam2}
 \end{align}
and
 \begin{align} \nonumber
    \lambda_3^k&= \int_{Q_T}\sum\limits_{i,n}  \sgn(U_i^{k,n}-U^k(s,y))f(U^k(s,y)) \left(\nu^k\left(\boldsymbol{c}_{i+1/2}^{k,n,\delta}\right)-\nu^k\left(\boldsymbol{c}_{i-1/2}^{k,n,\delta}\right)\right)\\ & \qquad \times \int\limits_{C^{n}} \Phi(s,y,t,x_{i+1/2})  \d t \d s \d y  \nonumber\\
    &\quad +\int_{Q_T}\sum\limits_{i,n}  \sgn(U_i^{k,n}-U^k(s,y))f(U^k(s,y))\nonumber \\
    & \quad \quad  \times 
    \int_{C_i^n}\mathcal{U}_x^{k,\Delta}(t,x)  \left(\Phi(s,y,t,x)-\Phi(s,y,t,x_{i+1/2})\right) \d x \d t  \d y \d s \nonumber\\
    &\quad + \int_{Q_T}\sum\limits_{i,n}  \sgn(U_i^{k,n}-U^k(s,y))f(U^k(s,y))\nonumber \\ 
    & \quad \quad \times 
\int_{C_i^n}\left(\mathcal{U}_x^{k,\Delta}(t,x)  -\frac1{\Delta x}\left(\nu^k\left(\boldsymbol{c}_{i+1/2}^{k,n,\delta}\right)-\nu^k\left(\boldsymbol{c}_{i-1/2}^{k,n,\delta}\right)\right)\right)\Phi(s,y,t,x_{i+1/2}) \d x \d t \d y \d s\nonumber\\ \nonumber
    &\quad :=\overline{\lambda}_3^{k}+\mathcal{E}_{31}^k+\mathcal{E}_{32}^k.\\& \label{lam3} 
\end{align}
To complete the proof of the theorem, it remains to prove the following claims:
\begin{enumerate}[\textbf{Claim \arabic*}]
    % \item 
        \item \label{Cl1}: $\lambda_{11}^{k}+\overline{\lambda}_2^{k}=\mathcal{O}\left(\displaystyle\frac{\Delta x}{\epsilon}+\displaystyle\frac{\Delta t}{\epsilon_0} \right)$
    \item \label{Cl2}:$\lambda_{12}^{k}+\overline{\lambda}_3^{k}=\mathcal{O}\left(\displaystyle\frac{\Delta x}{\epsilon}+\displaystyle\frac{\Delta t}{\epsilon_0} +\D t + \delta\right)$
     \item \label{Cl3}: $\mathcal{E}_2^k=\mathcal{O}\left(\displaystyle\frac{\Delta x}{\epsilon}+\displaystyle\displaystyle\frac{\delta}{\epsilon}\right)$
    \item \label{Cl4}: $\mathcal{E}_{31}^k+ \mathcal{E}_{32}^k=\mathcal{O}\left(\displaystyle\frac{\Delta x}{\epsilon}+\displaystyle\displaystyle\frac{\delta}{\epsilon}\right)$
\end{enumerate}
 Note that the aim is to get the estimates, in terms of both $\Delta x, \Delta t$ and $\delta$. Also, since \ref{Cl1} depends only on $\Delta x$ and $\Delta t$, and not on $\delta,$ it can be essentially done on the lines of \cite[Lemma 3.3]{AHV2023}, since \begin{align}\label{cdiff}
   \sum\limits_i| c^{j,k,n}_{i+1/2} - c^{j,k,n}_{i-1/2}|\le \norma{U_{0}^k}_{L^1(\R)}\abs{{\mu}^{j,k}}_{BV(\R)}\norma{\Gamma^{j,k}}_{L^1(\R^+)},
\end{align} by summing \eqref{eq:c2} over $i\in\Z$. Note that \ref{Cl2} can be essentially done on the lines of Claim 2 of \cite[Lemma 3.3]{AHV2023} provided that $\sum\limits_i \Big|
\bigl( c^{j,k,n}_{i+1/2} - c^{j,k,n}_{i-1/2} \bigr)
- \bigl( c^{j,k,n-1}_{i+1/2} - c^{j,k,n-1}_{i-1/2} \bigr)
\Big|$ does not depend on $\displaystyle\frac{1}{\delta}$. Infact, in what follows we prove that the following holds: \begin{align}\label{cd2}
&\sum\limits_i \Big|
\bigl( c^{j,k,n}_{i+1/2} - c^{j,k,n}_{i-1/2} \bigr)
- \bigl( c^{j,k,n-1}_{i+1/2} - c^{j,k,n-1}_{i-1/2} \bigr)
\Big| \le 
\mathcal{C}_{14}^k\, (\Delta t+\delta),
\end{align} which is a non trivial and requires the additional assumption (cf.~\ref{Moment}) on first moment of $\Gamma^{j,k}$ . 
 % Let \[\Gamma_{\delta}^{j,k,r}=\frac{1}{\Delta t}\int_{C^r}\Gamma^{j,k}_{\delta}(\tau)\d \tau, r\in\mathcal{N}_T.\]
%  G^{q} := \frac{1}{\Delta t}\int_0^{t^{q+1}} \Gamma^{j,k}_{\delta}(\tau)\, d\tau= \sum\limits_{r=0}^q \, \Gamma_{j,k,\delta}^{r}, q\ge0.\] 
% % Then, since $\Gamma_{j,k,\delta}^{r} \ge 0,$
% $G^{q+1} - G^{q}
% = \, \Gamma_{\delta}^{q+1}\ge 0,$  and 
% $
% 0 \le G^{q}
% \le \displaystyle\frac{1}{\Delta t}\int_0^\infty \Gamma^{j,k}_{\delta}(t)\, dt
% = 1.$
Note that
\[
\sum\limits_{m\in\mathcal{N}_T} m\Delta t\,\Gamma_{\delta}^{j,k,m}
= \sum\limits_{m\in\mathcal{N}_T}m\int_{C^m}\Gamma^{j,k}_{\delta}(\tau)\,d\tau.
\]
% where $\Gamma_{\delta}^{j,k,r}=\frac{1}{\Delta t}\int_{C^r}\Gamma^{j,k}_{\delta}(\tau)\d \tau.$
For every $\tau\in C^m,$ we have $t_m\le \tau$.
Using the nonnegativity of $\Gamma^{j,k}_{\delta}$, this implies
\[
m\Delta t\,\Gamma^{j,k}_{\delta}(\tau)
\ge \tau\,\Gamma^{j,k}_{\delta}(\tau).
\]
Therefore,
\begin{align*}
\sum\limits_{m\in\mathcal{N}_T} m\Delta t\,\Gamma_{\delta}^{j,k,m}
&\le \frac{1}{\Delta t}
\sum\limits_{m\in\mathcal{N}_T}\int_{C^m}
\tau\,\Gamma^{j,k}_{\delta}(\tau)\,d\tau= \frac{1}{\Delta t}\int_{0}^{\infty}
\tau\,\Gamma^{j,k}_{\delta}(\tau)\,d\tau=\frac{\delta}{\Delta t}\int_{0}^{\infty}\theta\,\Gamma^{j,k}(\theta)\,d\theta.
\end{align*}
Using \eqref{Moment}, we have,
\begin{align}\label{mo}
    \sum\limits_{m\ge 1} m\Delta t\,\Gamma_{\delta}^{j,k,m}
 \le \delta \frac{C_{\boldsymbol{\Gamma}}}{\Delta t},
\sum\limits_{m\ge 1} \Delta t\,\Gamma_{\delta}^{j,k,m}
 \le \delta \frac{C_{\boldsymbol{\Gamma}}}{\Delta t}.
\end{align}
Observe that,
\[
c^{j,k,n}_{i+\frac12}
=
\Delta x\,\Delta t
\sum\limits_{m=0}^n
\sum\limits_{p\in\mathbb Z}
\Gamma^{j,k,n-m}_\delta\,
\mu^{j,k}_{i+\frac12-p}\,
U^{k,m}_{p+1} =
\Delta x\,\Delta t
\sum\limits_{m=0}^{n}
\sum\limits_{p\in\mathbb Z}
\Gamma^{j,k,m}_\delta\,
\mu^{j,k}_{i+\frac12-p}\,
U^{k,n-m}_{p+1},
\]
which implies that
\begin{align}
c^{j,k,n}_{i+\frac12}-c^{j,k,n}_{i-\frac12}
&=
\Delta x\,\Delta t
\sum\limits_{m=0}^n
\sum\limits_{p\in\mathbb Z}
\Gamma^{j,k,m}_\delta
\bigl(
\mu^{j,k}_{i+\frac12-p}-\mu^{j,k}_{i-\frac12-p}
\bigr)
U^{k,n-m}_p,
\label{eq:jump-n}
\end{align}
and 
% \medskip
% \noindent
% \textbf{Step 2: Spatial jump at time $n-1$.}
% Similarly,
\begin{align}
c^{j,k,n-1}_{i+\frac12}-c^{j,k,n-1}_{i-\frac12}
&=
\Delta x\,\Delta t
\sum\limits_{m=0}^{n-1}
\sum\limits_{p\in\mathbb Z}
\Gamma^{j,k,m}_\delta
\bigl(
\mu^{j,k}_{i+\frac12-p}-\mu^{j,k}_{i-\frac12-p}
\bigr)
U^{k,n-1-m}_p .
\label{eq:jump-n-1}
\end{align}
Subtracting \eqref{eq:jump-n-1} from \eqref{eq:jump-n} yields
\begin{align}
&\bigl( c^{j,k,n}_{i+\frac12}-c^{j,k,n}_{i-\frac12} \bigr)
-
\bigl( c^{j,k,n-1}_{i+\frac12}-c^{j,k,n-1}_{i-\frac12} \bigr)
\\&=
\Delta x\,\Delta t
\Bigg[
\sum\limits_{m=0}^{n-1}\Gamma^{j,k,m}_\delta
\sum\limits_{p}
\bigl(
\mu^{j,k}_{i+\frac12-p}-\mu^{j,k}_{i-\frac12-p}
\bigr)(U^{k,n-m}_p-U^{k,n-1-m}_p)
 \nonumber\\
&\quad 
+
\sum\limits_{p}
\Gamma^{j,k,n}_\delta
\bigl(
\mu^{j,k}_{i+\frac12-p}-\mu^{j,k}_{i-\frac12-p}
\bigr)
U^{k,0}_p
\Bigg].
\label{eq:raw-difference}
\end{align}
Then, using \ref{lem:L1t}, we have \eqref{cd2}, 
% \begin{align}
% &\sum\limits_i\bigl|c^{j,k,n}_{i+\frac12}-c^{j,k,n}_{i-\frac12} 
% -
% \bigl( c^{j,k,n-1}_{i+\frac12}-c^{j,k,n-1}_{i-\frac12}\bigr) \bigr|
% \nonumber\\
% &=
% \Delta t\,
% \abs{\mu^{j,k}}_{\bv(\R)}\mathcal{C}_9^k
% +
% \,\frac{\delta C_{\boldsymbol{\Gamma}}}{\lambda}
% \abs{\mu^{j,k}}_{\bv(\R)}
% \norma{{\boldsymbol{U}}^{0}}_{(L^1(\R))^N},
% \label{eq:raw-difference}
% \end{align}
with $\mathcal{C}_{14}^k:=
\abs{\mu^{j,k}}_{\bv(\R)}\mathcal{C}_9^k
+
\,\displaystyle\frac{C_{\boldsymbol{\Gamma}}}{\lambda}
\abs{\mu^{j,k}}_{\bv(\R)}
\norma{{\boldsymbol{U}}^{0}}_{(L^1(\R))^N},$ which completes the proof of \ref{Cl2}. To prove \ref{Cl3},
consider the term,
\begin{align*} & \nonumber \sum\limits_{i,n} \int_{C_i^n} \left|\nu^k((\boldsymbol{\mu}\circledast\boldsymbol{U}^{\Delta}_{\delta}(t))^k)(x)-\nu^k\left(\boldsymbol{c}_{i+1/2}^{k,n,\delta}\right)\right|\d t\d x\\
&=\sum\limits_{i}\sum\limits_{n=0}^{n=n_{\delta} } \int_{C_i^n}\left|\nu^k((\boldsymbol{\mu}\circledast\boldsymbol{U}^{\Delta}_{\delta}(t))^k)(x)-\nu^k\left(\boldsymbol{c}_{i+1/2}^{k,n,\delta}\right)\right|\d t\d x\\
&\qquad+\sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \int_{C_i^n}\left|\nu^k((\boldsymbol{\mu}\circledast\boldsymbol{U}^{\Delta}_{\delta}(t))^k)(x)-\nu^k\left(\boldsymbol{c}_{i+1/2}^{k,n,\delta}\right)\right|\d t\d x\\
&=\mathcal{E}_{21}^k+\mathcal{E}_{22}^k,
\end{align*}
 {where $n_{\delta}\in \mathcal{N}_T$ is taken to be the smallest integer such that $n_{\delta}\Delta t\geq\delta.$}
%\vspace{-3mm}
Note that,
\begin{align}
 \mathcal{E}_{21}^k
 % &=
 % {\color{black}\sum\limits_{i}\sum\limits_{n=0}^{n=n_{\delta} } \int_{C_i^n}\left|\nu^k((\boldsymbol{\mu}\circledast\boldsymbol{U}^{\Delta}_{\delta}(t))^k)(x)-\nu^k\left(\boldsymbol{c}_{i+1/2}^{k,n,\delta}\right)\right|\d t\d x \nonumber} {line can be removed if necessary} \\
&\le\abs{\nu^k}_{\lip(\R)}\sum\limits_{i}\sum\limits_{n=0}^{n=n_{\delta} }\sum\limits_{p\in\Z}\sum\limits_{j\in\mathcal{N}}\int_{C_i^n}
 \bigg| \int_{C_p}\mu^{j,k}(x-\xi)  U^{j,n}_{p,\delta}\d \xi -\Delta x \D t \sum\limits_{m=0}^n \Theta^{j,k,n-m}_{i+1/2-p,\delta} U^{j,m}_{p,\delta}\bigg| \d t\d x  \nonumber \\
&\le \abs{\nu^k}_{\lip(\R)}\sum\limits_{i}\sum\limits_{n=0}^{n=n_{\delta} }\sum\limits_{p\in\Z}\sum\limits_{j\in\mathcal{N}}\int_{C_i^n}
 \int_{C_p}\mu^{j,k}(x-\xi)  U^{j,n}_{p,\delta}\d \xi \d t\d x \nonumber \\
&\qquad+\Delta x \D t \abs{\nu^k}_{\lip(\R)}\sum\limits_{i}\sum\limits_{n=0}^{n=n_{\delta} }\sum\limits_{p\in\Z}\sum\limits_{j\in\mathcal{N}}\sum\limits_{m=0}^n\int_{C_i^n} \Theta^{j,k,n-m}_{i+1/2-p,\delta} U^{j,m}_{p,\delta} \d t\d x  \nonumber
\\
&\le 2\abs{\nu^k}_{\lip(\R)}(\delta+\Delta t)\norma{\boldsymbol{U_0}}_{(L^1(\R))^{N}}\norma{\boldsymbol{\mu}}_{(L^1(\R))^{N^2}} +\abs{\nu^k}_{\lip(\R)}(\delta+\Delta t)\norma{\boldsymbol{U_0}}_{(L^1(\R))^{N}}\norma{\boldsymbol{\mu}}_{(L^1(\R))^{N^2}}\nonumber\\
&:=\mathcal{C}_{21}^k(\delta+\Delta t).\nonumber\\&\label{S1}\end{align}
To estimate $\mathcal{E}_{22}^k,$ the idea is to invoke the fact that, for any $t\ge \delta,$ $\displaystyle\int_0^t\Gamma^{j,k}_{\delta}(\tau)d\tau=1,$ which implies $\Delta t\displaystyle\sum\limits_{m=0}^n\Gamma^{j,k,m}_{\delta}=1$ for any $n\ge n_{\delta}.$
Thus,  \begin{align*} \allowdisplaybreaks
    % \label{S2}
\mathcal{E}_{22}^k&= \sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{j\in\mathcal{N}}\int_{C_i^n}
 \bigg|\nu^k \bigg(\sum\limits_{p\in\Z} \int_{C_p}\mu^{j,k}(x-\xi)  U^{j,n}_{p,\delta}\d \xi \bigg) -\nu^k \bigg(\Delta x \D t \sum\limits_{m=0}^n\sum\limits_{p\in\Z} \Theta^{j,k,n-m}_{i+1/2-p,\delta} U^{j,m}_{p,\delta}\bigg)\bigg| \d t\d x \\
%  &
% \leq\abs{\nu^k}_{\lip(\R)}\sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{j\in\mathcal{N}}\sum\limits_{p\in\Z}\int_{C_i^n}
%  \bigg|\int_{C_p}\mu^{j,k}(x-\xi)  U^{j,n}_{p,\delta}\d \xi -\Delta x \D t \sum\limits_{m=0}^n \Theta^{j,k,n-m}_{i+1/2-p,\delta} U^{j,m}_{p,\delta}\bigg| \d t\d x\\&
&\le \abs{\nu^k}_{\lip(\R)}\sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{j\in\mathcal{N}}\int_{C_i^n}\bigg|\sum\limits_{p\in\Z}\int_{C_p}\mu^{j,k}(x-\xi)  U^{j,n}_{p,\delta}\d \xi -\Delta x \D t \sum\limits_{m=0}^n \Theta^{j,k,n-m}_{i+1/2-p,\delta} U^{j,m}_{p,\delta}\bigg|  \\&
 \le \abs{\nu^k}_{\lip(\R)}
\sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{j\in\mathcal{N}}\\&
\qquad\times\int_{C_i^n}\bigg|\Delta t\sum\limits_{m=0}^n\Gamma^{j,k,m}_{\delta}\sum\limits_{p\in\Z}\int_{C_p}\mu^{j,k}(x-\xi) U^{j,n}_{p,\delta}\d \xi -\Delta x \D t \sum\limits_{m=0}^n \mu^{j,k}_{i+1/2-p}\Gamma^{j,k,m}_{\delta} U^{j,n-m}_{p,\delta}\bigg| \d t\d x \\&
\le \abs{\nu^k}_{\lip(\R)}\Delta t
\sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{m=0}^n \\& \qquad \times \Gamma^{j,k,m}_{\delta}\sum\limits_{j\in\mathcal{N}}\sum\limits_{p\in\Z}\int_{C_i^n}\bigg|\int_{C_p}\mu^{j,k}(x-\xi)   U^{j,n}_{p,\delta}\d \xi -\Delta x  \mu^{j,k}_{i+1/2-p} U^{j,n-m}_{p,\delta}\bigg| \d t\d x, 
\end{align*}
which implies,
\begin{align*}
\mathcal{E}_{22}^k&\le \abs{\nu^k}_{\lip(\R)}\Delta t\sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{m=0}^n\Gamma^{j,k,m}_{\delta}\sum\limits_{j\in\mathcal{N}}\sum\limits_{p\in\Z}\int_{C_i^n}
\bigg|\int_{C_p}\mu^{j,k}(x-\xi)   U^{j,n}_{p,\delta}\d \xi-\Delta x \mu^{j,k}_{i+1/2-p} U^{j,n}_{p,\delta}\bigg|\\
&\qquad+\abs{\nu^k}_{\lip(\R)}\bigg|\Delta x \mu^{j,k}_{i+1/2-p} U^{j,n}_{p,\delta}-\Delta x \mu^{j,k}_{i+1/2-p} U^{j,n-m}_{p,\delta}\bigg|\\
&\le \abs{\nu^k}_{\lip(\R)}\Delta t\sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{m=0}^n\Gamma^{j,k,m}_{\delta}\sum\limits_{j\in\mathcal{N}}\sum\limits_{p\in\Z}\int_{C_i^n}
\bigg|\int_{C_p}\mu^{j,k}(x-\xi)   U^{j,n}_{p,\delta}\d \xi-\int_{C_p} \mu^{j,k}_{i+1/2-p} U^{j,n}_{p,\delta}\d \xi\bigg|\\\
&\qquad+\abs{\nu^k}_{\lip(\R)}\bigg|\Delta x \mu^{j,k}_{i+1/2-p} U^{j,n}_{p,\delta}-\Delta x \mu^{j,k}_{i+1/2-p} U^{j,n-m}_{p,\delta}\bigg| \\
&\le \abs{\nu^k}_{\lip(\R)}\Delta t\sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{m=0}^n\Gamma^{j,k,m}_{\delta}\sum\limits_{j\in\mathcal{N}}\sum\limits_{p\in\Z}\int_{C_i^n}\int_{C_p}\abs{\mu^{j,k}(x_{i+1/2-p})-\mu^{j,k}(x-\xi)}U^{j,n}_{p,\delta}\d \xi \d\tau\d t\d x\\
&\qquad+\abs{\nu^k}_{\lip(\R)}\Delta t\sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{m=0}^n\Gamma^{j,k,m}_{\delta}\sum\limits_{j\in\mathcal{N}}\Delta x\sum\limits_{p\in\Z}\abs{U^{j,n}_{p,\delta}-U^{j,n-m}_{p,\delta}}\int_{C_i^n}\mu^{j,k}(x_{i+1/2-p}) \d t\d x
\\&=  \abs{\nu^k}_{\lip(\R)}\mathcal{E}_{221}^k+\abs{\nu^k}_{\lip(\R)}\mathcal{E}_{222}^k.
% \\
% &:=\mathcal{C}_{22}(\delta+\Delta x)
\end{align*}
Now, a direct estimate yields 
\begin{align*}
% \label{e_221}
    \mathcal{E}_{221}^k\le N \Delta x\abs{\mu^{j,k}}_{BV(\R)}  \norma{\boldsymbol{U}_0}_{L^1(\R^N)}T:=\mathcal{C}_{221}^k\Delta x.
    \end{align*}
It should be noted that a direct estimate on $\mathcal{E}_{222}^k$ will yield a term $1/\delta$, which does not serve the purpose. Instead, 
in what follows, we invoke the moment estimates \eqref{Moment} to estimate $\mathcal{E}_{222}^k$. Firstly, we note that
% \[
% \sum\limits_{m\in\mathcal{N}_T} m\Delta t\,\Gamma^{j,k,m}_{\delta}
% = \sum\limits_{m\in\mathcal{N}_T}m\int_{C^m}\Gamma^{j,k}_{\delta}(\tau)\,d\tau .
% \]
% For every $\tau\in C^m,$ we have $t_m\le \tau$.
% Using the nonnegativity of $\Gamma^{j,k}_{\delta}$, this implies
% \[
% m\Delta t\,\Gamma^{j,k}_{\delta}(\tau)
% \le \tau\,\Gamma^{j,k}_{\delta}(\tau).
% \]
% Therefore,
% \begin{align*}
% \sum\limits_{m\in\mathcal{N}_T} m\Delta t\,\Gamma^{j,k,m}_{\delta}
% &\le \frac{1}{\Delta t}
% \sum\limits_{m\in\mathcal{N}_T}\int_{C^m}
% \tau\,\Gamma^{j,k}_{\delta}(\tau)\,d\tau= \frac{1}{\Delta t}\int_{0}^{\infty}
% \tau\,\Gamma^{j,k}_{\delta}(\tau)\,d\tau=\frac{\delta}{\Delta t}\int_{0}^{\infty}\theta\,\Gamma^{j,k}(\theta)\,d\theta.
% \end{align*}
% Using \eqref{Moment}, we have,
% \begin{align}\label{mo}
%     \sum\limits_{m\in\mathcal{N}_T} m\Delta t\,\Gamma^{j,k,m}_{\delta}
%  \le C_{\boldsymbol{\Gamma}}\,\frac{\delta}{\Delta t}.
% \end{align}
% % .\]  
using \eqref{mo} and \ref{lem:L1t} in $\mathcal{E}_{222}^k$, we have
% \begin{align}
%     \sum\limits_{m=0}^n m \Gamma^{j,k,m}_{\delta} \le \frac{C_{\boldsymbol{\Gamma}} \delta}{(\D t)^2},
% \end{align}
% resulting in
\begin{align}
\begin{split} \label{e_222}
\mathcal{E}_{222}^k 
% &=\Delta t\sum\limits_{i}\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{m=0}^n\Gamma^{j,k,m}_{\delta}\sum\limits_{j\in\mathcal{N}}\Delta x\sum\limits_{p\in\Z}\abs{U^{j,n}_{p,\delta}-U^{j,n-m}_{p,\delta}}\int_{C_i^n}\mu^{j,k}(x_{i+1/2-p}) \d t\d x \nonumber\\
    &=\Delta t\Delta t\sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{m=0}^n\Gamma^{j,k,m}_{\delta}\sum\limits_{j\in\mathcal{N}}\Delta x\sum\limits_{p\in\Z}\abs{U^{j,n}_{p,\delta}-U^{j,n-m}_{p,\delta}}\norma{\mu^{j,k}}_{L^1(\R)}\\
    % &=\Delta t^2 \D x \norma{\mu^{j,k}}_{L^1(\R)} \sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{m=0}^n\Gamma^{j,k,m}_{\delta}\sum\limits_{j\in\mathcal{N}}\sum\limits_{p\in\Z}\abs{U^{j,n}_{p,\delta}-U^{j,n-m}_{p,\delta}} \nonumber 
    % \\
    &=\Delta t^3 \norma{\mu^{j,k}}_{L^1(\R)} \sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{m=0}^n\Gamma^{j,k,m}_{\delta}\sum\limits_{j\in\mathcal{N}} m \mathcal{C}_9^k
        =\Delta t^3  N  \mathcal{C}_9^k\norma{\mu^{j,k}}_{L^1(\R)} \sum\limits_{n=n_{\delta}+1}^{n=N_T} \sum\limits_{m=0}^n m \Gamma^{j,k,m}_{\delta}
\\
    &=  \Delta t  N  \mathcal{C}_9^k\norma{\mu^{j,k}}_{L^1(\R)} \sum\limits_{n=n_{\delta}+1}^{n=N_T} C_{\boldsymbol{\Gamma}} \delta \nonumber =N\mathcal{C}_9^k\norma{\mu^{j,k}}_{L^1(\R)} TC_{\boldsymbol{\Gamma}}  \delta:=\mathcal{C}_{222}^k\delta
    \end{split}
\end{align}
Now, combining the above estimates, we get: 
\begin{align*}
&fds\nonumber\sum\limits_{i,n} \int_{C_i^n} \left|\nu^k((\boldsymbol{\mu}\circledast\boldsymbol{U}^{\Delta}_{\delta}(t))^k)(x)-\nu^k\left(\boldsymbol{c}_{i+1/2}^{k,n,\delta}\right)\right|\d t\d x \\ &\le \mathcal{C}_{21}^k(\delta+\Delta x)+\abs{\nu^k}_{\lip(\R)}\mathcal{C}_{221}^k\Delta x+\abs{\nu^k}_{\lip(\R)}\mathcal{C}_{222}^k\delta.
\end{align*}
Finally, using the following bounds for every $(t,x) \in Q_T$, \begin{align*}\int_{Q_T}\abs{p_{i,\delta}^{k,n}(U^k(s,y))} \d y \d s &\le \abs{f^k}_{\lip(\R)}
\norma{U^{k}_0}_{L^1(\R)},
\int_{Q_T}\abs{\Phi_x(s,y,t,x)} \d y \d s \le \displaystyle\frac{1}{\epsilon}, 
\end{align*}
we obtain that
\begin{align*}
\nonumber\abs{\mathcal{E}_2^k}&\le \abs{f^k}_{\lip(\R)}
\norma{U^{k}_0}_{L^1(\R)}\left(\mathcal{C}_{21}^k\displaystyle\frac{\delta}{\epsilon}+\lambda\mathcal{C}_{21}^k\displaystyle\frac{\Delta x}{\epsilon}+\abs{\nu^k}_{\lip(\R)}\mathcal{C}_{221}^k\frac{\Delta x}{\epsilon}+\abs{\nu^k}_{\lip(\R)}\mathcal{C}_{222}^k\displaystyle\frac{\delta}{\epsilon}\right),
\end{align*}  
which completes the proof of \ref{Cl3}. 
Further, note that
$\mathcal{E}^k_{31}$ and  $\mathcal{E}^k_{32}$ do not depend on $\norma{\Gamma_{\delta}^{j,k}}_{L^{\infty}(\R)}$ and only depends on $\norma{\Gamma_{\delta}^{j,k}}_{L^{1}(\R)},$ and hence, the proof of \ref{Cl4} can be handled on the same lines of \ref{Cl3}, (see also $\mathcal{E}_{31}$ and $\mathcal{E}_{32}$ in \cite[Lemma 3.3]{AHV2023}). To complete the proof, firstly we set 
$\varepsilon =\max(\sqrt{\delta},\sqrt{\Delta x})$ and $  \varepsilon_0 = \sqrt{\Delta t}.$ Now, note that  \ref{lem:L1t} implies $
\gamma(U^{k,\Delta}_{\delta}, \sqrt{\Delta t}) = \mathcal{O}(\sqrt{\Delta t})$. 
and \eqref{init} implies 
$
\|\boldsymbol{U}_0^\Delta - \boldsymbol{U}_0\|_{(L^1(\mathbb{R}))^{N}} = \mathcal{O}(\Delta x).$ Finally, the desired estimate follows from combining the results from \ref{Cl1}-\ref{Cl4} with Lemma \ref{kuz1} and 
the choice of $\epsilon$ and $\epsilon_0$.
\end{proof}
\section{Numerical Experiments}
\label{num1}
We present numerical experiments to illustrate the theory developed in \S\ref{NLL}, highlighting the memory-to-memoryless dynamics and the asymptotic compatibility of the finite volume scheme \eqref{scheme2}. Throughout this section, we choose $\beta = 0.3333$ and $\lambda = 0.1286$ so as to satisfy the CFL condition \eqref{CFL_LF}.
We consider a {nonlocal-in-space and nonlocal-in-time} generalization of the Keyfitz–Kranzer system introduced in \cite{ACG2015} in one spatial dimension, given by 
\begin{equation}
  \label{eq:kk}
  \left\{
    \begin{array}{l}
      \partial_t U^1 + \partial_x \left(U^1 \,  \nu (\Theta_{\delta}*U^1,\Theta_{\delta}*U^2)\right) = 0
      \\
      \partial_t U^2 + \partial_x \left( U^2 \,  \nu (\Theta_{\delta}*U^1,\Theta_{\delta}*U^2)\right) = 0
    \end{array}
  \right.,
\end{equation} where
  % \begin{align*}
$ \Gamma_{\delta}(t)=\displaystyle\frac{3}{\delta^3}(\delta-t)^2\mathbbm{1}_{(0,\delta)}(t), \mu(x)=\displaystyle Lx(\eta-x)^3\mathbbm{1}_{(0,\eta)}(x),\Theta_{\delta}(t,x)=\mu(x)\Gamma_{\delta}(t)$, and $\nu(a,b)=(1-a^2-b^2)^3$ where $L$ is such that $\displaystyle\int_{\R}\mu(x)\d x=1.$
% \end{align*}
 The system~\eqref{eq:kk} fits into the framework of this article  with $N=2, \boldsymbol{\Theta}_{\delta} =
    \left[\begin{array}{ccc}
        \Theta_{\delta} & \Theta_{\delta}
        \\
\Theta_{\delta}& \Theta_{\delta}
      \end{array}\right],\nu^k(x)=\nu(x),$ and  $f^k(u)=u,$ and that $\displaystyle\int_{\R^+}\Gamma(\tau)\d \tau=1,$ which is specifically required for \S\ref{NLL}. 
      


We compute numerical solutions of \eqref{eq:kk} on the domain
 $[-5, \, 5]$ and the time
interval $[0, \, 0.5]$ with
\begin{align}
    \label{eq:ex1} U^1_0(x)=0.25\mathbbm{1}_{(-2,2)}(x), \quad &
    U^2_0(x)=\mathbbm{1}_{(-2,2)}(x).
    \end{align}\\
    
Figure \ref{fig:ex211} displays the numerical approximations of \eqref{eq:kk}-\eqref{eq:ex1} generated by the numerical  
scheme \eqref{scheme2}, 
with $\Delta x =0.00625, \eta=0.25$ and  $\delta=0.0125$. It can be seen that the numerical scheme is able to capture both shocks and rarefactions well. 
\begin{figure}[h!]
 \centering
\includegraphics[width=\textwidth,keepaspectratio]{Pictures/u_at_00625_5.png}
% \end{subfigure}
\hfill
\caption{Solution to the nonlocal conservation law~\eqref{eq:kk}-\eqref{eq:ex1} on the domain $[-5,\,5]$ at times $t =
    0.00,\; 0.017,\;0.33, \: 0.5$, with mesh size $\Delta x=0.00625$. $U^1$({\full}),\,\,$U^2$({\color{red}\dashed}).}
  \label{fig:ex211}
\end{figure}

 \begin{figure}[h!]
  \centering \noindent\begin{minipage}{0.46\textwidth}
    \centering
    \begin{tabular}{|c|c|c|c|c|c|c|c|c|c|}\hline
     \multicolumn{1}{|c|}{ $ \delta$}&\multicolumn{1}{|c|}{$\frac{e_{\delta}(T)}{100}$}\vline & \multicolumn{1}{|c|}{$\alpha$}\vline\\
     \hline
     $4/5$&$31.11$&\tabularnewline
     \hline
     $2/5$&$19.01$&$0.71$\tabularnewline
     % \hline
     % \hline
     % \backslashbox{$\Delta x$}{Initial Data}
     % &&\tabularnewline
     \hline
     $1/5$&$9.63$&$0.98$\tabularnewline
     \hline
     $1/10$&$4.83$&$0.99$\tabularnewline
     \hline
     $1/20$&$2.41$&$1.00$\tabularnewline
     \hline
     $1/40$&$1.17$&$1.04$\tabularnewline
     \hline
     % \hline
     $1/80$&$0.604$&$0.96$\tabularnewline
     \hline
 \end{tabular}
  \end{minipage}
\noindent\begin{minipage}{0.4\textwidth}
\includegraphics[width=\textwidth, trim = 40 25 20 5]{Pictures/error_1D_NM_M.png}
  \end{minipage}  \caption{Convergence rate $\alpha$ for the memory-to-memoryless dynamics of solution $\boldsymbol{U}_{\delta}(T)$ with decreasing $\delta$:  Domain $[-5,\,5]$ at time $T=0.5$ for the problem~\eqref{eq:kk}-\eqref{eq:ex1}. Observed convergence rate({\color{blue}\oline}), theoretical convergence rate ({orange}), and reference line of slope $1$({\color{green}\dashed}).}\label{fig:ex21}
\end{figure}\begin{figure}[ht!]
 \centering
% \begin{subfigure}{.45\textwidth}
\includegraphics[width=\textwidth,keepaspectratio]{Pictures/decreasing_delta.png}
\caption{Domain $[-5,\,5],   T=0.5,\Delta x =0.00625,\eta=0.25$: Solution to the ~\eqref{eq:kk}-\eqref{eq:ex1} with decreasing time convolution radii $\delta=$ $0.8$({\color{black}\chainn}),$0.4$({\color{magenta}\chainn}),$0.2$({\color{magenta}\chainn}), $0.1$({\color{cyan}\dashed}), $0.0125$({\color{green}\dotted}); Solution to the nonlocal-space only counterpart of ~\eqref{eq:kk}, with initial data \eqref{eq:ex1}({\color{blue}\full}).}
  \label{fig:ex22}
\end{figure}
 Figures \ref{fig:ex21}--\ref{fig:ex22} illustrate the memory-to-memoryless dynamics of \eqref{eq:kk}--\eqref{eq:ex1} as captured by the numerical scheme. To this end, we compute numerical approximations of \eqref{eq:kk}--\eqref{eq:ex1} using \eqref{scheme2} with $\Delta x = 0.00625$ and $\eta = 0.25$, while successively decreasing the temporal convolution radius $\delta$, starting from $\delta = 0.0125$ and halving it at each step. As shown in Figure \ref{fig:ex21}, the entropy solutions of the nonlocal space--nonlocal time system \eqref{eq:kk} converge to the entropy solution of the corresponding nonlocal-space-only system as the radius of the temporal convolution kernel $\Gamma$ tends to zero.

Let $\boldsymbol{U}_{\delta}(T,\cdot)$ denote the numerical solution at time $T$ corresponding to the temporal convolution radius $\delta$, computed using \eqref{scheme2} for the nonlocal space--nonlocal time system \eqref{eq:kk}--\eqref{eq:ex1} and let $\boldsymbol{U}(T,\cdot)$ of the nonlocal-space-only counterpart of \eqref{eq:kk}. In addition, we estimate the convergence rate of the memory-to-memoryless dynamics at time $T = 0.5$ 
 by measuring $
e_{\delta}(T) = \norma{\boldsymbol{U}_{\delta}(T,\cdot) - \boldsymbol{U}(T,\cdot)}_{(L^1(\mathbb{R}))^N}.$
The observed convergence rate is given by $
\alpha = \displaystyle\log_{2}\!\left(\frac{e_{\delta}(T)}{e_{\delta/2}(T)}\right),$
and is reported in Figure \ref{fig:ex22}. We observe that $\alpha > 0.5$, exceeding the theoretical rate established in Theorem~\ref{con}.

Figures \ref{fig:ex31}–\ref{fig:ex32} demonstrate the asymptotic compatibility of the scheme \eqref{scheme2} in the memory-to-memoryless limit. Numerical approximations of \eqref{eq:kk}–\eqref{eq:ex1} are computed with $\eta = 0.25$ using \eqref{scheme2}, \begin{figure}[h!]
  \centering \noindent\begin{minipage}{0.46\textwidth}
    \centering
    \begin{tabular}{|c|c|c|c|c|c|c|c|c|c|}\hline
     \multicolumn{1}{|c|}{ $ \frac{\Delta x}{0.0125}$}&\multicolumn{1}{|c|}{$e_{\Delta}(T)$}\vline & \multicolumn{1}{|c|}{$\alpha$}\vline\\
     \hline
      $1$&$0.63$&\tabularnewline
     \hline
     $1/2$&$0.38$&$0.72$\tabularnewline
     \hline
     $1/4$&$0.19$&$0.99$\tabularnewline
     % \hline
     % \hline
     % \backslashbox{$\Delta x$}{Initial Data}
     % &&\tabularnewline
     \hline
     $1/8$&$0.096$&$1.00$\tabularnewline
    \hline
     % $1/16$&$2.41$&$1.00$\tabularnewline
     % \hline
     % $1/40$&$1.17$&$1.04$\tabularnewline
     % \hline
     % % \hline
     % $1/80$&$0.604$&$0.96$\tabularnewline
     % \hline
 \end{tabular}
  \end{minipage}
\noindent\begin{minipage}{0.4\textwidth}
\includegraphics[width=\textwidth, trim = 40 25 20 5]{Pictures/error_1D_NM_M_dh.png}
  \end{minipage}  
  \vspace{1cm}\caption{Convergence rate $\alpha$ for the asymptotic compatibility of the scheme \eqref{scheme2} for memory-to-memoryless dynamics:  Domain $[-5,\,5]$ at time $T=0.5$ for the problem~\eqref{eq:kk}-\eqref{eq:ex1}. Observed convergence rate({\color{blue}\oline}), theoretical convergence rate ({orange}), and reference line of slope $1$({\color{green}\dashed}).}\label{fig:ex31}
\end{figure}\begin{figure}[ht!]
 \centering
% \begin{subfigure}{.45\textwidth}
\includegraphics[width=\textwidth,keepaspectratio]{Pictures/decreasing_deltah.png}
\caption{Domain $[-5,\,5],   T=0.5,\Delta x =0.00625,\eta=0.25$, Solution to ~\eqref{eq:kk}-\eqref{eq:ex1} with decreasing $\Delta x$.
$\frac{\Delta x}{0.0125}=$ $1$({\color{black}\chainn}),$1/2$({\color{magenta}\chainn}),$1/4$({\color{magenta}\chainn}), $1/8$({\color{green}\dashed}); Solution to the nonlocal-space only counterpart of ~\eqref{eq:kk}, with initial data \eqref{eq:ex1}({\color{blue}\full}).}
  \label{fig:ex32}
\end{figure}while the spatial grid is successively refined. Starting from $\Delta x = 0.0125$, the mesh size is halved at each refinement step. Simultaneously, the temporal convolution radius $\delta$ is reduced in such a way that the ratio $\displaystyle \frac{\delta}{\Delta x} = 128$ remains fixed. As evidenced in Figure \ref{fig:ex31}, the entropy solutions of the nonlocal space–nonlocal time system \eqref{eq:kk} converge to the entropy solution of the corresponding nonlocal-space-only system in the limit $\delta \to 0$. Let $\boldsymbol{U}_{\delta}^{\Delta}(T,\cdot)$ denote the numerical solution at time $T$, corresponding to temporal convolution radius $\delta$ and spatial mesh size $\Delta x$, computed using \eqref{scheme2} for the nonlocal space--nonlocal time system \eqref{eq:kk}--\eqref{eq:ex1}. 
Let $\boldsymbol{U}^{\Delta_{\text{fine}}}(T,\cdot)$ denote the numerical solution at time $T$ of the corresponding nonlocal-space-only system, computed using \eqref{scheme2} on the finest spatial grid with mesh size $\Delta_{\text{fine}} = 0.0125/4$, which is taken as the reference solution. 
In addition, the convergence rate at time $T = 0.5$ is estimated by computing the $L^1$-error with respect to this reference solution. Specifically, we define $
e_{\Delta}(T) = \norma{\boldsymbol{U}_{\delta}^{\Delta}(T,\cdot) - \boldsymbol{U}^{\Delta_{\text{fine}}}(T,\cdot)}_{(L^1(\mathbb{R}))^N}.$
The observed convergence rate is then given by $
\alpha = \log_{2}\!\left(\frac{e_{\Delta}(T)}{e_{\Delta/2}(T)}\right)$. The computed rates are reported in Figure \ref{fig:ex32}. We observe that $\alpha > 0.5$, which exceeds the theoretical convergence rate established in Theorem~\ref{rate}.
\section{Conclusion and Future Directions}
In this work, using convergent finite volume approximations together with the continuous dependence estimates for scalar conservation laws with smooth coefficients, we prove well-posedness of the initial value problem \eqref{nlm}--\eqref{init}. As the temporal kernel concentrates, the entropy solutions of \eqref{nlm}--\eqref{init} converge to those of the purely spatially nonlocal system \eqref{nls}, \eqref{init}, with rate $\mathcal{O}(\sqrt{\delta})$, thereby justifying the memory-to-memoryless limit. For temporal kernels with a finite first moment, the finite volume schemes for \eqref{nlm}--\eqref{init} are shown to be compatible with this asymptotic behavior, with an asymptotic rate of $\mathcal{O}(\sqrt{\delta}+\sqrt{\Delta x})$. To the best of our knowledge, these are the first results addressing well-posedness and asymptotic analysis for such general systems with memory.

Stability estimates, error analysis of the proposed finite volume method, and extensions to less regular interaction kernels in the presence of source terms will be presented in forthcoming companion papers.  For the case of  $N=1$ and linear $f$, we also plan to investigate the asymptotic compatibility of the finite volume schemes \eqref{scheme2} for the nonlocal-to-local transition from \eqref{nlm}–\eqref{init} to \eqref{local}, \eqref{init}. Nevertheless, several challenging problems remain open:
\begin{itemize}
\item When nonlocality acts only in time (without spatial convolution) and the flux $f^k$ is nonlinear in \eqref{nlm}--\eqref{init}, the entropy framework and the spatial $\bv$ bounds do not directly carry over, since the spatial regularity of the nonlocal term is lost, and the system behaves like a local conservation law with discontinuous flux. Consequently, a general well-posedness theory for such PDEs, as well as the corresponding nonlocal-to-local asymptotic analysis, remain {\color{black}a} largely open problem at the time of writing, even for $N=1$.
{\color{black}However, for $N=1$, and $f$ linear, we believe that one could possibly prove the existence and uniqueness of the weak solutions (without additional entropy condition)} using fixed-point arguments.
\item With $N>1$, the complete passage from  \eqref{nlm}-\eqref{init} to fully local system \eqref{local}, \eqref{init} for general nonlinear fluxes is also largely open at this time, as the {\color{black}well-posedness theory for }local system, \eqref{local},\eqref{init} with $N>1$ is again underdeveloped for general $\bv$ data. {\color{black}Alternatively, one needs to curate a special class of nonlocal systems so that the corresponding local system is well-posed for $\bv$ initial data.}
\end{itemize}
% We believe that the framework introduced here opens the door to a systematic mathematical theory for hyperbolic systems with simultaneous spatial nonlocality and temporal memory, and provides a foundation for further analytical and computational developments in this rapidly evolving area.
\bmhead{Acknowledgements}This work was partially supported by AA's Seed Money Grant SM/08/2025-26 and the ARG Matrics Grant ANRF/ARGM/2025/001976/MTR from the Anusandhan National Research Foundation (ANRF), India, as well as GV's INSPIRE Faculty Fellowship (IFA24-MA215) from the Department of Science and Technology (DST), Government of India. The authors also acknowledge the hospitality of the Department of Mathematics, Penn State University, where part of this work was completed during AA's visit and GV's postdoctoral tenure.
\bibliographystyle{siam}
\bibliography{references}


\end{document}
% \section{conclusion}
% By means of finite volume method and doubling of the variable technque we establihs hte well-posedness for the system of nonlocal conservation laws with memory and showed that the notion of the entropy solution proposed in this article is consistent with the spae only nonlocal conservation laws in the sense that as the support of the time kernel goes to zero the corresponding entropy solution converge to teh entropy soltuins of the nonlocal  in space conservation laws. If the nonlocal term involves only time convolution and no space convolution the notion of entropy solution proposed in this article does not carry forward as the term $\mathcal{U}$ is differentiable in the space variable. However, one can choose a particular class of $f$ for example linear in the local part and can prove the uniqueness of the weak solution itself by employing fixed point argument and hope to prove the limit from conservation laws with memory to its memoryless conterpart(scalar conservation laws) which we aim to explore in one of our upcomng article.  In the scalar case one can also prove the schems are asymtotic compatible to local conservation laws.

% {May be list them as open questions and say we aim to answer them one by one in our upcoming works}

% \section{Analysis in several dimensions}
% In this section, we briefly discuss the applicability of our analysis in several space dimensions using dimension-splitting technique:
% We consider the conservation law 
% \begin{align*}
% U^k_t+\sum\limits_{i=1}^d \partial_{x_i}(f^i(U^k)\nu^i(\Theta^i*U^{k}))=0 \qquad (t,x) \in [0,T] \times \R^d
% \end{align*}
% \begin{definition}\label{ent:d}
%     A function $u\in C([0,T];L^1(\R^d;[0,1]))\cap L^{\infty}(\R^d \times [0,T])$  is an entropy solution of the IVP~\eqref{eq:kk}--\eqref{IVP:data}, 
% if for every $k\in\R,$ and for all non-negative $\phi\in C_c^{\infty}([0,T)\times \R^d)$,
% \begin{align} \label{kruz:d}
% \begin{split}
% &\int_{\R^d} \int_0^T |U^k(t,x)-\alpha|\phi_t\d t \d x \\&+\int_{\R^d} \int_0^T \sum\limits_{i=1}^d \sgn(U^k(t,x)-\alpha) (f^i(U^k(t,x))-f^i(\alpha))\nu^k(\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x)))\phi_{x_i} \d t \d x\\ 
% &-\int_{\R^d} \int_0^T \sum\limits_{i=1}^d \sgn (U^k(t,x)-\alpha)f^k(\alpha)\partial_{x_i}(\nu^k(\nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x)))\phi \d t \d x \\&  +\int_{\R^d} |U_{0}^k(x)-\alpha|\phi(0,x) \d x \geq 0,
% \end{split}
% \end{align}
% where for every $(t,x)\in \overline [0,T]\times \R ^d,$
% % \begin{align}\label{mc}
% %\begin{split}
%     $ \nu^k((\boldsymbol{\Theta}\circledast \boldsymbol{U})^k(t,x))=(\Theta*u)(t,x).$
%      % \\  &=\displaystyle\int_0^t\int_{\R}U^k(\tau,x-\xi)\mu^{j,k}(\xi)\Gamma^{j,k}(t-\tau) \d \tau \d \xi.
% %\end{split}
% % \end{align}
% \end{definition}

% \begin{enumerate}[label=(\textbf{B\arabic*})]
% 	\item \label{B1} $f^i\in \lip(\R)$  with $ f^k(0)=0$ and $f^k(1)=1$ 
%  % \item $ \nu^k \in (C^2 \cap   \operatorname{BV}  \cap \, W^{2,\infty}) (\R),$
%  \item \label{B2} $\Theta^i(t,x)=\mu^{j,k}(x) \Gamma^{j,k}(t)$, where the space kernel $\boldsymbol{\mu} \in C^2(\R) \cap W^{2,\infty}(\R^d)$ and the time kernel $\Gamma\in C^2([0,\infty);\R^+) \cap W^{2,\infty}([0,\infty);\R^+)$,
%  \item  \label{B3} $\nu\in C^2(\R) \cap W^{2,\infty}(\R)$ with $\nu^k(0)=0,$ {\color{black}non-negative Or remove Godunov scheme}
% \end{enumerate} 
% and for every $(t,x)\in [0,T] \times \R^d$, \begin{align}\label{mc}
% \begin{split}
%    (\Theta*u)(t,x)&:=\displaystyle\int_0^t\int_{\R} U^k(\tau,\xi)\mu^{j,k}(x-\xi)\Gamma^{j,k}(t-\tau) \d \tau \d \xi.
%      % \\  &=\displaystyle\int_0^t\int_{\R}U^k(\tau,x-\xi)\mu^{j,k}(\xi)\Gamma^{j,k}(t-\tau) \d \tau \d \xi.
% \end{split}
% \end{align}

% case of two space
% dimensions and denote the space variables by $(x,y) \in
% \R^2$, and consider the following PDE:
% \begin{align*}
% % \label{eq:1}
% \partial_t u +
% \partial_x (f^1(U^k)\nu^1(\Theta^1*u))
% + \partial_y (f^2(U^k)\nu^2(\Theta^2*u))
% = 0.
% \end{align*}
% Further, for numerical scheme, fix a rectangular grid with sizes $\Delta x$ and $\Delta y$ in
% $\R^2$ and choose a time step $\Delta t$. For later use, we also
% introduce the usual notation
% \begin{equation*}
%   (t^n, x_i,y_j) = (n\Delta t,i\Delta x, j \Delta y), \quad
%   n\in\N,\, i, j\in \Z, \quad
%     \lambda_x  = \frac{\Delta t}{\Delta x},  \,
%     \lambda_y  =  \frac{\Delta t}{\Delta y}. 
% \end{equation*}
% Throughout,  we fix initial data $U_{0}^k\in (L^{\infty}\cap \operatorname{BV}) (\R^2;
% [0,1])$ and introduce
% \[
%   u^{0}_{ij}
%   =
%   \frac{1}{\Delta x \, \Delta y}
%   \int_{x_{i-1/2}}^{x_{i+1/2}} \int_{y_{j-1/2}}^{y_{j+1/2}}
%   U_{0}^k(x,y) \, \d{y}\, \d{x} 
%   \quad \mbox{ for } i,j \in \Z.
% \]
% We define a piecewise constant approximate solution $U^{k,\Delta}$ 
% by
% \[
%   U^{k,\Delta}(t,x,y) =  u^n_{ij}\chi_{[t^n, t^{n+1}) \times[x_{i-1/2},x_{i+1/2})\times [y_{j-1/2},y_{j+1/2})}(t,x,y),  \quad
%      n\in\N, \,  i,j \in  \Z,
%  \]
%  where $\chi_A$ denotes the indicator function of a set $A$, 
% through the following marching formula based on dimensional splitting,
% (see~\cite[Sec.~3]{CrandallMajda1980Monotone} and \cite[Sec.~5]{HKLR2010} for details):
% \begin{align*}
%   % \label{eq:2} 
%     u^{n+1/2}_{ij}
%     & = 
%     u^n_{ij} - \lambda_x \big(
%    \mathcal{F}^{x,n}_{i+1/2,j} (U^{k,n}_{ij},u^n_{i+1,j}) - 
%    \mathcal{F}^{x,n}_{i-1/2,j} (U^{k,n}_{i-1,j},u^n_{ij})
%      \big),
%     \\[6pt]  \nonumber
%     u^{n+1}_{ij}
%     & = 
%     u^{n+1/2}_{ij}  - 
% \lambda_y \big(
%    \mathcal{F}^{y,n}_{i,j+1/2} (U^k{n+1/2}_{ij},u^{n+1/2}_{i,j+1})
% - \mathcal{F}^{y,n}_{i,j-1/2} (U^k{n+1/2}_{i,j-1},u^{n+1/2}_{ij})
%     \big),
% \end{align*}
% where $\mathcal{F}^{x,n}_{i+1/2,j}$ and  $\mathcal{F}^{y,n}_{i,j+1/2}$ denote the numerical approximations of the fluxes $f^1(U^k) \nu^1(\Theta^1*u)$ and $f^2(U^k) \nu^2(\Theta^2*u)$ at the interfaces $(x_{i+1/2},y_j)$ and $(x_{i},y_{j+1/2})$, respectively, for $i,j\in \Z$.
% The convolution terms are computed through quadrature formula, i.e.,
% \begin{align}
%     c^{x,n}_{i+1/2, j}
%     &=  \Delta x \Delta y \D t \sum\limits_{k=0}^n\sum\limits_{l,p\in\Z} \Theta^{1,n-k}_{i+1/2-p,j-l} U^{k}_{p,l} \\
%     % &
%     % \Delta x \, \Delta y
%     %   \sum\limits_{l,p \in \Z} 
%     %   \mu^{1}_{i+1/2-l, j-p}  \nu^1(U^{k,n}_{l+1/2, p}), \\
%     c^{y,n}_{i, j+1/2}
%     &= \Delta x \Delta y \D t \sum\limits_{k=0}^n\sum\limits_{l,p\in\Z} \Theta^{2,n-k}_{i-p,j+1/2-l} U^{k}_{p,l},
%     % \Delta x \, \Delta y
%     %   \sum\limits_{l,p \in \Z}
%     %   \mu^2_{i+1/2-l, j-p}   \nu^2(U^{k,n}_{l+1/2, p}) ,
% \end{align}
% where, 
% % \begin{equation*}
%   % \label{eq:etatheta}
% $\Theta^k_{i,j,n} = \Theta^k (x_i, y_j,t^n),k=1,2,i,j\in\Z,n\in\mathbb{N}.$
% % \end{equation*}
% Throughout, we require that $\Delta t$ is chosen in order to satisfy
% the CFL conditions
% \begin{align}
%    \label{CFL_LF1}
%    \begin{split}
% \lambda_x & \le \frac{\min(1, 4-6\alpha_x,6\alpha_x )}{1+6\abs{f^1}_{\lip(\R)}\norma{\nu^1}_{L^\infty(\R)}},\\
%   \lambda_y & \le \frac{\min(1, 4-6\alpha_y,6\alpha_y )}{1+6\abs{f^2}_{\lip(\R)}\norma{\nu^2}_{L^\infty(\R)}}, \quad \quad 
%   \alpha_x,\alpha_y \in \left(0,\frac{2}{3} \right),
%   \end{split}
% \end{align}
% and 
% \begin{equation*}
%    \lambda _x\abs{f^1}_{\lip(\R)}\norma{\nu^1}_{L^\infty(\R)}\leq \frac12, \quad
%    \lambda _y\abs{f^2}_{\lip(\R)}\norma{\nu^2}_{L^\infty(\R)}\leq \frac12,
% \end{equation*}
%    with numerical fluxes $\mathcal{F}^x$ or $\mathcal{F}^y$ chosen as 
%    Lax--Friedrichs flux and Godunov flux, respectively. Extension to other monotone fluxes and for higher dimensions is similar. The numerical scheme can now be shown to converge to entropy solution,  see, for example, \cite{ACG2015}.
%    For the sake of completeness we briefly state the key results in this set up.

% **Some gyan about\$\bv$ space in 2D and introduce the notaionts**
%    \begin{lemma}[Compactness]
%    \begin{align*}
%    &\sum\limits_{i,j \in Z} \abs{u^n_{i+1,j}-u^n_{i,j}} \D y + \abs{u^n_{i,j+1}-u^n_{i,j}} \D x \\ & \quad \leq \exp (K t^n) \sum\limits_{i,j \in Z} \abs{u^0_{i+1,j}-u^0_{i,j}} \D y + \abs{u^0_{i,j+1}-u^0_{i,j}} \D x + K\frac{\exp(Kt)-1}{K}
%    \end{align*}
%    \end{lemma}

% \begin{theorem}[Well-posedness]
% The IVP admits a unique entropy solution and the numerical approximations $u^{\D}$ generated by the dimension splitting algorithm converge in $L^1_{\loc}([0,T] \times \R^d)$ to the  entropy solution $U^k$ of the IVP.
% \end{theorem}

%     \begin{theorem}\label{con} Let $U^k_{\delta},u$ be the entropy solutions of the IVPs
% \begin{align}\label{1'}
%     \partial_tu_{\delta}+ \partial_x (f^k(U^k_{\delta})\nu^k(\Theta_{\delta}*U^k_{\delta}))&=0,\\
%     % U^k_{\delta}(0,x)&=U_{0,{\delta}}(x)
%    \label{2'} \partial_tu+ \partial_x (f^k(U^k)\nu^k(\mu*u))&=0,
%    \end{align}
%    with initial data
%    \begin{align}
%    \label{3'}  u(0,x)=U_{\delta}(0,x)&=U_{0}(x)
% \end{align}
% respectively. Then, for any time $T>0$, the following convergence rate estimate holds:
% \begin{align*}
%     \norma{U^k_{\delta}(T)-U^k(t)}_{L^1(\R)}=\mathcal{O}(\sqrt{\delta}).
% \end{align*}
% \end{theorem}












% % \section{Numerical Experiments}
% % \label{num}
% % We now present some numerical experiments to illustrate the theory presented in the previous section. Throughout the section, $\alpha$ is chosen to be $0.3333$, and $\lambda$ is chosen to be $0.1$ so as to satisfy the CFL condition \eqref{CFL_LF}.

% % We employ the IVP \eqref{eq:kk},\eqref{IVP:data} with
% % $f^k(U^k)=u, \nu^k(U^k)=1-u$ and 
% % \[ {\color{black}
% % \Gamma^{j,k}(x)=\mu^{j,k}(x)=L(x({\delta}-x))^{3}\mathbbm{1}_{(0,{\delta})}(x)}.\]Further, $L$ is chosen such that $\int_{\R}\mu^{j,k}(x)\d{x}=1.$ 
% % % \begin{table}[ht!]{
% % %  \centerline{
% % %    \begin{tabular}{|c|c|c|c|c|c|c|c|c|c|}\hline
% % %      \multicolumn{1}{|c|}{}&\multicolumn{2}{|c|}{${\color{black}e_{\Delta x}(T)}$}\vline & \multicolumn{2}{|c|}{${\color{black}\alpha}$}\vline\\
% % %      \hline
% % %      \backslashbox{${\color{black}\frac{\Delta x}{0.00625}}$}{$f$}
% % %      & $f^k(U^k)=u$ & $f^k(U^k)=u(1-u)$&   $f^k(U^k)=u$ & $f^k(U^k)=u(1-u)$\tabularnewline
% % %      \hline
% % %      ${\color{black}1}$&  $0.0358$&$0.0381$&$0.5354$&$0.5238$\tabularnewline
% % %      \hline
% % %      ${\color{black}1/2}$
% % %      &$0.0247$ &$0.0265$&$0.6355$&$0.6236$ \tabularnewline
% % %      \hline
% % %      ${\color{black}1/4}$
% % %      &$0.0159$&$0.0172$&$0.6124$&$ 0.6983$\tabularnewline
% % %      \hline
% % %      ${\color{black}1/8}$
% % %      &$0.0104$ &$0.0106$&&\tabularnewline
% % %      \hline
% % % \end{tabular}}}
% % % \caption{Convergence rate $\alpha$ for the numerical scheme~\eqref{apx}-\eqref{c_i}  for the approximate solutions
% % %   to the problem~\eqref{eq:kk}, \eqref{eq:ex1} on the domain $[-5,\,5]$ at time $T=0.5.$ }\label{Table82}
% % % \end{table}
% % % \begin{figure}[h!]
% % % \centering\includegraphics[width=.9\textwidth,keepaspectratio]{Paper1/NM_2182023/Pictures/error_1D_AHV1.jpg}
% % %     \caption{Convergence rate $\alpha$ for the numerical scheme~\eqref{apx}-\eqref{c_i}  for the approximate solutions
% % %   to the problem~\eqref{eq:kk}, \eqref{eq:ex1} on the domain $[-5,\,5]$ at time $T=0.5.$ .}
% % %    \label{fig:my_label111}
% % % \end{figure}
% % This PDE fits the hypothesis of the article.
% % Further, the domain of integration is chosen to be the interval $[-1.5, 1.5]$ with $t\in[0, 0.5]$, and 
% % % with $$f^k(U^k)=u, \beta^k(x,u)=s^k(x)u, \mu^{j,k}(x)=\frac{3}{\epsilon^3}(\epsilon-x)^2\mathbbm{1}_{(0, \epsilon)}(x)$$ where $s^k(x)$ is chosen appropriately so that the flux $\boldsymbol{f}$ satisfies (H0)-(H2).
% % \begin{eqnarray}
% %     \label{eq:ex1} U_{0}^k(x)=0.25\mathbbm{1}_{(-0.9,0.1)}(x)+0.5\mathbbm{1}_{(0.1,0.3)}(x).
% % \end{eqnarray}Figure \ref{fig:ex212} displays the numerical approximations of \eqref{eq:kk}, \eqref{eq:ex1} generated by the numerical scheme \eqref{scheme2}-\eqref{eq:conv},
% % with $\Delta x=0.00625,$ and ${\color{black}{\delta}=0.125,{\delta}=0.0125}$ and compares it with the numerical approximations  of \eqref{local},\eqref{init}, \eqref{eq:ex1} generated by the standard Lax-Friedrich's scheme
% % with $\Delta x=0.00625.$ It can be seen that the numerical scheme is able to capture both shocks and rarefactions well, with a slight difference between the dynamics of local and nonlocal solutions. 
% % \begin{figure}[h!]
% %  \centering
% % \begin{subfigure}{.45\textwidth}
% % \includegraphics[width=\textwidth,keepaspectratio]{Paper1: Nonlocal conlaws with memory/Amorim/Figure_4.png}
% % \end{subfigure}
% % % \hfill
% % % \begin{subfigure}{.45\textwidth}
% % % \includegraphics[width=.75\textwidth,keepaspectratio]{Paper1/NM_2182023/Pictures/L0.png}
% % % \end{subfigure}\hspace{1cm}
% % \begin{subfigure}{.45\textwidth}
% % \includegraphics[width=.75\textwidth,keepaspectratio]{Paper1: Nonlocal conlaws with memory/Amorim/p0001.png}
% % \end{subfigure}
% % % \hfill
% % % \begin{subfigure}{.45\textwidth}
% % % \includegraphics[width=.75\textwidth,keepaspectratio]{Paper1/NM_2182023/Pictures/NL1.png}
% % % \end{subfigure}\hspace{1cm}
% % \begin{subfigure}{.45\textwidth}
% % \includegraphics[width=.75\textwidth,keepaspectratio]{Paper1: Nonlocal conlaws with memory/Amorim/p0002.png}
% % \end{subfigure}
% % % \hspace{1cm}
% % % \begin{subfigure}{.45\textwidth}
% % % \includegraphics[width=.75\textwidth,keepaspectratio]{Paper1/NM_2182023/Pictures/NL2.png}
% % % \end{subfigure}
% %  \begin{subfigure}{.45\textwidth}
% % \includegraphics[width=.75\textwidth,keepaspectratio]{Paper1: Nonlocal conlaws with memory/Amorim/p0003.png}
% %  % \caption{$f^k(U^k)=u$}
% %  % \label{linear}
% % \end{subfigure}
% % \hfill
% % % \begin{subfigure}{.45\textwidth}
% % % \includegraphics[width=.75\textwidth,keepaspectratio]{Paper1/NM_2182023/Pictures/NL3.png}
% % %  \caption{$f^k(U^k)=u(1-u)$}
% % %  \label{nonlinear}
% % % \end{subfigure}
% % \caption{Solution to the nonlocal conservation law~\eqref{eq:kk},\eqref{eq:ex1} ({\color{blue}\full}) and the local conservation law ~\eqref{local},\eqref{init},\eqref{eq:ex1} ({\color{black}\chain}) on the domain $[-1.5,\,1.5]$ at times $t =
% %     0.00,\; 0.017,\;0.33, \: 0.5$, with mesh size $\Delta x=0.00625$.}
% %   \label{fig:ex212}
% % \end{figure} \\
% % \begin{figure}[h!]
% %  \centering
% % % \begin{subfigure}{.45\textwidth}
% % % ÷\begin{subfigure}{.45\textwidth}÷÷
% % \includegraphics[width=.75\textwidth,keepaspectratio]{Paper1: Nonlocal conlaws with memory/Amorim/NLNL_forward.png}
% % % \end{subfigure}÷
% % \caption{Domain $[-1.5,\,1.5],  T=0.3$: Solution to the ``localtime-nonlocal space" conservation law, \eqref{nls}, \eqref{eq:ex1} ({\color{black}\chainn}); Solution to the nonlocal conservation law~\eqref{eq:kk}, \eqref{eq:ex1} with decreasing time-convolution radii ${\delta}$.}
% %   \label{fig:ex211}
% % \end{figure}
% % % represents the behavior of the solutions with non-linear $f^k(U^k)=u(1-u),$ with zeros at $u=0$ and $u=1.$ It can be seen that the density $U^k$ always lies within the interval $[0,1]$ demonstrating the invariant region principle illustrated in ~\cite[Remark 2.3]{AmorimColomboTeixeira} and \cite[Example 2]{betancourt2011nonlocal}. 
% % Figure \ref{fig:ex211} illustrates the theory established in \S\ref{NLL}. It displays the numerical approximations of \eqref{eq:kk}, \eqref{eq:ex1} generated by the numerical scheme \eqref{scheme2}-\eqref{eq:conv},
% % with $\Delta x=0.00625,$ and ${\delta}=0.125$, and with
% % decreasing time-convolution radii ${\delta}$, starting with ${\delta}=200\Delta t$.  It compares these numerical approximations with the numerical approximations of ``nonlocal space-local time": \eqref{nls}, \eqref{eq:ex1} generated by the Lax-Friedrich's scheme of \cite{ACG2015}
% % with $\Delta x=0.00625,$ and ${\delta}=0.125$.  It can be seen that as illustrated in \S\ref{NLL}, the numerical solutions of ``nonlocal space-non local time": \eqref{eq:kk}, \eqref{eq:ex1} converge to the numerical solutions of `nonlocal space-local time': \eqref{nls}, \eqref{eq:ex1} as the convolution radius ${\delta}\rightarrow0.$