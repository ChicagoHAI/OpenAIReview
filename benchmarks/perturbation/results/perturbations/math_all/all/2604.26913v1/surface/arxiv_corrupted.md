\documentclass[a4paper,11pt,abstract=on]{scrartcl}


% \usepackage{amssymb}
% \usepackage{amsmath}
% \usepackage{amsthm}

% \usepackage{mathtools}
% \usepackage{etextools}
% \usepackage{ifthen}

% \usepackage{bbm}

% \usepackage{pgfplots}

% \usepackage{algorithm}
% \usepackage[noend]{algpseudocode}

% \usepackage{hyperref}

% \usepackage{booktabs}
% \usepackage{multirow}
% \usepackage{multicol}
% \mathtoolsset{showonlyrefs}

% \usepackage{threeparttable}

% \usepackage{nicefrac,xfrac}

% \usepackage{tikz}

\usepackage[T2A]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[russian,english]{babel}

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
\usepackage{hyperref}
\usepackage{caption}
\captionsetup{format=plain, justification=raggedright, singlelinecheck=false}
\allowdisplaybreaks

%%%%
% bib data
\usepackage[
backend=biber,
style=numeric-comp,
giveninits,
]{biblatex}
\addbibresource{sn-bibliography.bib}
%%%%
% additional packages

\usepackage{mathtools}
% \usepackage{etextools}
\usepackage{enumitem}
\usepackage{bbm}
\usepackage{nicefrac}
\usepackage{threeparttable}
\usepackage{tikz}

\newcommand{\lineblue}{%
  \tikz[baseline=-0.75ex] \draw[-, blue, very thick] (0,0) -- (1,0);%
}
\newcommand{\linepurple}{%
  \tikz[baseline=-0.75ex] \draw[-, purple!70!black, very thick] (0,0) -- (1,0);%
}
\newcommand{\lineorange}{%
  \tikz[baseline=-0.75ex] \draw[-, orange, very thick] (0,0) -- (1,0);%
}
\newcommand{\linegray}{%
  \tikz[baseline=-0.75ex] \draw[-, gray, very thick] (0,0) -- (1,0);%
}
\newcommand{\linegraydashed}{%
  \tikz[baseline=-0.75ex] \draw[dashed, gray, very thick] (0,0) -- (1,0);%
}
\newcommand{\linegraydotted}{%
  \tikz[baseline=-0.75ex] \draw[dotted, gray, very thick] (0,0) -- (1,0);%
}
\newcommand{\linereddashed}{%
  \tikz[baseline=-0.75ex] \draw[dashed, red, very thick] (0,0) -- (1,0);%
}


%% short cuts 

\DeclareMathOperator{\sign}{sign}
\DeclareMathOperator{\diag}{diag}
\DeclareMathOperator*{\argmax}{argmax}
\DeclareMathOperator*{\argmin}{argmin}
\DeclareMathOperator*{\spec}{spec}
\DeclareMathOperator*{\dist}{dist}
\DeclareMathOperator*{\trace}{tr}
\DeclareMathOperator*{\tT}{T}
\DeclareMathOperator*{\rank}{rank}
\DeclareMathOperator*{\spa}{span}
\DeclareMathOperator*{\grad}{grad}
\DeclareMathOperator*{\hess}{Hess}

\newcommand{\symA}{A^{\textup{H}}}
\newcommand{\symC}{C^{\textup{H}}}
\newcommand{\mgeq}{\succcurlyeq}
\newcommand{\scp}[2]{\left\langle{#1}, {#2}\right\rangle}
\newcommand{\scpF}[2]{\left\langle{#1}, {#2}\right\rangle_{\textup F}}
\newcommand{\scpB}[2]{\left\langle{#1}, {#2}\right\rangle_B}
\newcommand{\scpC}[2]{\left\langle{#1}, {#2}\right\rangle_{\bb C}}
\newcommand{\bb}{\mathbb}
\newcommand{\mc}{\mathcal}
\newcommand{\mf}{\mathfrak}
\DeclarePairedDelimiter{\abs}{\vert}{\vert}
\DeclarePairedDelimiter{\absC}{\vert}{\vert_{\CC}}
\DeclarePairedDelimiter{\norm}{\|}{\|}
\DeclarePairedDelimiter{\normB}{\|}{\|_{B}}
%%

\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}{Proposition}[section]
\newtheorem{corollary}{Corollary}[section]
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{remark}{Remark}[section]
\newtheorem{assumption}{Assumption}[section]
\newtheorem{example}{Example}[section]



\begin{document}



\title{Generalization of Zeroth-Order Method for Quotients of Quadratic Functions}


\author{Jonas Bresch\thanks{Technische Universität Berlin, Straße des 17. Juni 136, Berlin, 10587, Germany} \\
{\footnotesize\href{mailto:bresch@math.tu-berlin.de}{bresch@math.tu-berlin.de}}
}

\maketitle

\begin{abstract}
Optimization of quadratic functions 
and the quotient of those 
are relevant in subspace and iterative optimization methods.
In this paper,
the calculation of the generalized operator norm 
and extremal generalized Rayleigh quotient
is considered.
In contrast to recent works 
an unconstrained sampling approach 
on the entire sphere for the random search direction 
in each iteration is proposed. 
Furthermore,
the link to zeroth-order methods 
for Riemannian first- and second-order optimization methods is provided 
in the sense that the Riemannian gradient and Hessian
are estimated by the specific surrogates.
Even though the tangent space is not used in this construction
the optimal step size problem can be computed in a closed form.
The subproblems of this 
and recent works are illuminated in the context of 
sub-generalized Rayleigh quotient problems
on specific Gram matrices.
Together 
the achieved theory allows to construct an accelerated algorithm 
which shows state-of-the-art behavior 
and outperforms recent works.
\end{abstract}


\textbf{Keywords.}
operator norm $\cdot$
Rayleigh quotient $\cdot$
Riemannian optimization $\cdot$
zeroth-order $\cdot$
first-order $\cdot$
second-order $\cdot$
unbiased estimator $\cdot$
Riemannian manifold $\cdot$
generalized sphere

\textbf{MSC.} 65F35 $\cdot$  
15A60 $\cdot$ 
68W20 



\section{Introduction}
\label{sec: intro}

The computation of extremal spectral quantities of linear operators under restricted access models 
remains a fundamental challenge in applied mathematics, scientific computing, and data analysis. 
Quantities such as the operator norm, generalized Rayleigh quotients, numerical radius, 
and pseudospectral measures govern stability, transient amplification, and admissible step sizes 
in optimization and inverse problems 
\cite{TikArs43,TikArs77,trefethen2005spectrapseudospectra,ryu2022large,chambolle2011first,bredies2022degenerate}. 
In particular, for non-normal operators, eigenvalues alone fail to capture transient growth phenomena, 
making Rayleigh-type extremal formulations and pseudospectral diagnostics indispensable 
\cite{trefethen1999spectrapseudospectra,farrell1996generalizedstabilitytheorypartIInonautonomousoperators}.

A central object in this context is the generalized Rayleigh quotient,
which generalizes the operator norm and appears in a variety of applications. 
In statistics and machine learning, it underlies \textit{linear discriminant analysis} (LDA) 
and \textit{signal-to-noise ratio} (SNR) optimization, 
where between-class and within-class covariance matrices 
define operators \(A\) and \(B\) \cite{fisher1936taxonomic, rao1948bioclassification}. 
In signal processing, related formulations arise in beamforming and detection theory 
\cite{vantrees2002optimumarray}.
In inverse problems and PDE-constrained optimization, generalized Rayleigh quotients govern stability 
constants and convergence rates when weighted norms or preconditioners are involved 
\cite{engel2001aemigroups,lorenz2023chambolle}. 
Despite their importance, computing these quantities becomes highly nontrivial 
when only black-box access to the operators is available.

\paragraph*{Adjoint-free and matrix-free constraints.}
In many modern applications, linear maps \(A : \bb R^d \to \bb R^m\) and \(B : \bb R^d \to \bb R^\ell\) 
are accessible only through forward evaluations. 
This setting arises, for example, in large-scale PDE solvers, time-stepping schemes, 
tomographic forward models, and legacy simulation codes 
\cite{benner2020operatorinference,Savanier2021ProximalGA,gunzburger2002perspectives,lorenz2018randomized}. 
In such scenarios, forming matrices, computing adjoints, or inverting operators is infeasible. 
Moreover, discretized adjoints may be inconsistent with the forward operator, 
leading to unreliable results in classical adjoint-based schemes 
\cite{trefethen2005spectrapseudospectra,huber2025convergence,fikl2016comprehensive,luchini2014adjointequation,luchini2024adjointequation}. 
These constraints rule out standard methods such as power-schemes, 
Lanczos procedures, and Krylov subspace methods, 
which rely on repeated adjoint applications or dense linear algebra 
\cite{krylov1921,lanczos1950,parlett1998symmetriceigenvalueproblem,knyazev2001matrixfreekrylovpcgmethod}.
Relying on inexact adjoints \cite[§~1]{chan1998transpose} 
for reducing numerical complexity \cite[§~2.9]{gunzburger2002perspectives}
in the computations \cite[§~28~\&~48,~p.~446]{trefethen2005spectrapseudospectra}
introduces the so-called adjoint mismatch
as detailedly studied in \cite[§~1.1]{B8}.

This has motivated the development of \textit{zeroth-order} and \textit{derivative-free} methods, 
which use only function evaluations and random perturbations 
\cite{burke2002optimizingmatrixstability,li2023stochastic,balasubramanian2022zeroth}. 
Recent approaches combine random search, sketching, and consensus-based dynamics 
to approximate spectral quantities in a matrix-free fashion 
\cite{halko2011randomapproximatematrixdecomposition,riedl2024consensusbasedoptimization}. 
However, existing methods and novel, substantially improved algorithms \cite{B8,B9,B12}
for the operator norm, generalized Rayleigh quotient, and the adjoint mismatch, 
often rely on tangent-space sampling on manifolds, 
require access to adjoint operators or metric information, 
or employ heuristic curvature approximations.

\paragraph*{Unconstrained sampling and zeroth-order quasi-Newton methods.}
This work introduces a fundamentally different approach based on 
sampling on the entire unit sphere. 
Therefore, it can be seen as an unconstrained sampling approach compared to \cite{B8,B9,B12}.
Instead of drawing search directions from tangent spaces of a Riemannian manifold, 
we sample directions globally on the unit sphere,
which removes the need for conditional sampling or metric-dependent constructions. 
This seemingly simple modification has significant algorithmic consequences: 
it decouples the sampling step from the operators, 
simplifies implementation, 
and enables unbiased zeroth-order estimators 
for both gradient and curvature information.

Building on this sampling strategy, we develop a zeroth-order optimization framework 
for generalized Rayleigh quotient maximization that operates entirely with forward evaluations. 
The first component is a stochastic gradient estimator derived from random directional evaluations. 
The second and main novelty is a \textit{zeroth-order quasi-Newton method} 
in which the curvature model is given by an \emph{unbiased estimator of the Riemannian Hessian}. 
This distinguishes the approach from classical quasi-Newton methods, 
which rely on secant conditions or deterministic approximations 
\cite{gill1972quasinewton, Antoniou2007}. 
Here, curvature information is obtained directly from randomized function evaluations, 
yielding a principled second-order method in a fully derivative-free setting.


\paragraph*{Relevance.}
The improved methods \cite{B8,B9,B12} already
blend random search \cite{li2023stochastic,balasubramanian2022zeroth}, 
sketching \cite{li2014sketching}, 
slicing \cite{quellmalz2023slicing,quellmalz2024slicing}, 
projection \cite{li2023stochastic,boumal2023introduction}, 
and consensus-style \cite{riedl2024consensusbasedoptimization} updates 
to balance implementability for legacy and black-box codes 
with provable approximation behavior and empirical robustness 
in non-normal and ill-conditioned settings. 
%
The proposed generalization and extension 
for zeroth-order and derivative-free,
as well as curvature-based methods 
provide a viable path to reliable operator norms $\norm{A}$,
extremal Rayleigh quotient $\mc R(A,B)$, where $d = m = \ell$,
and generalized operator norm $\norm{A / B}$ diagnostics, 
and may also contribute to pseudospectral analysis.

\section{Preliminaries}
\label{sec: preliminaries}

In this section,
we introduce the considered problem of the generalized operator norm,
link it to the extremal generalized Rayleigh quotient,
and introduce tools for zeroth-, first-, and second-order 
Riemannian optimization techniques.

\subsection{Optimization Problem}
\label{sec: optimization problem}

The optimization problem 
\vspace{-5pt}
\begin{equation}
    \label{eq: prob}
    \norm{A/B} \coloneqq \min_{v \in \bb R^{d} \setminus \{0\}} \;
    \frac{\norm{A v}}{\norm{B v}}
\end{equation}
for two rectangular matrices $A \in \bb R^{m \times d}$
and $B \in \bb R^{\ell \times d}$,
which is considered in this paper,
is a generalization of the operator norm 
$\norm{A} \coloneqq \norm{A / I_d} = \max_{v \in \bb R^d \setminus \{0\}}
    \nicefrac{\norm{A v}}{\norm{v}}$
where $B = I_d$ is chosen.
Here, we have to guarantee that $B^{\tT}B \succ 0$,
so that \eqref{eq: prob} is well defined.
Hence, $\ell \leq d$ is a necessary assumption 
on the dimension of the space of the domain and range of $B$.
The sufficient condition on $B$
is equivalently given by $\det(B^{\tT}B) \neq 0$,
$\rank(B) = d$, or $\ker(B) = \{0\}$,
whenever $\ell \geq d$.
Considering the (generalized) spheres 
given by 
\begin{equation*}
    \label{eq: spheres}
    \bb S_D^{d-1} \coloneqq \{v \in \bb R^d \mid \norm{v}_D \coloneqq \sqrt{\scp{v}{D v}} = 1\},
    \quad \text{where} \quad 
    D \succ 0,
\end{equation*}
and we write for the unit sphere,
i.e. for $D = I_d$, $\bb S^{d-1} \coloneqq \bb S_{I_d}^{d-1}$,
yields 
\begin{equation}
    \label{eq: prop sphere gen}
    \norm{A/B}^2
    = \max_{v \in \bb R^d \setminus\{0\}} \;
    \frac{\scp{v}{A^{\tT}A v}}{\scp{v}{B^{\tT}B v}}
    = \max_{v \in \bb S^{d-1}} \;
    \frac{\scp{v}{A^{\tT}A v}}{\scp{v}{B^{\tT}B v}}
    = \max_{v \in \bb S_{A^{\tT}A}^{d-1}} \;
    \scp{v}{A^{\tT}A v}.
\end{equation}
%
The latter is due to the scale invariance of the considered (squared) objective
\begin{equation}
    \label{eq: obj}
    f(v) 
    \coloneqq \frac{\scp{v}{A^{\tT}A v}}{\scp{v}{B^{\tT}B v}}
    = \frac{\norm{A v}}{\norm{B v}}
\end{equation}
from \eqref{eq: prob}, respectively \eqref{eq: prop sphere gen}.
The function in \eqref{eq: obj}
is also known as the generalized Rayleigh quotient of $(A^{\tT}A, B^{\tT}B)$.
Furthermore, 
\eqref{eq: prob} is a generalization 
of the extremal generalized Rayleigh quotient computation 
$\mc R(C, D) \coloneqq 
\max_{v \in \bb R^d \setminus\{0\}} 
\frac{\scp{v}{C v}}{ \scp{v}{D v}}
= \max_{v \in \bb S_{D}^{d-1}} 
\scp{v}{C v}$,
where $C \in \bb R^{d \times d}$ is an arbitrary, quadratic matrix 
and $D \in \mathcal S_+^d$ is Hermitian positive definite,
considered in \cite{B9}.
Here, we denote
\begin{align*}
    \mc S_+^d \coloneqq 
    &\,\{X \in \mc S^d \mid \scp{v}{X v} > 0 \; \forall v \in \bb R^{d} \setminus\{0\}\} 
    \subset 
    \mc S^d \coloneqq \{X \in \bb R^{d \times d} \mid X = X^{\tT}\}.
\end{align*}
More precisely,
we have the following relation 
$\norm{A/ B}^2
= \mc R(A^{\tT}A, B^{\tT}B)$,
if 
$B^{\tT}B \succ 0$.
If we are not aware of the adjoint $B^{\tT}$ of $B$ \cite{chan1998transpose,trefethen2005spectrapseudospectra,gunzburger2002perspectives,B8}
then the computation and construction for solving 
the extremal generalized Raleigh quotient
and hence our considered problem \eqref{eq: prob} 
via the generalized $B^{\tT}B$-sphere, i.e. $\bb S_{B^{\tT}B}^{d-1}$,
from \cite{B9} can be not applied.
Therefore,
we focus on the optimization problem 
\begin{equation}
    \label{eq: prob sphere}
    \norm{A / B}^2 
    = \max_{v \in \bb S^{d-1}} \;
    f(v) 
    = \max_{v \in \bb S^{d-1}} \;
    \frac{\norm{A v}^2}{\norm{B v}^2},
\end{equation}
where we are also interested in the set of maximizer.


\subsection{Riemannian Optimization Techniques}
\label{sec: riemannian optimization}

The problem \eqref{eq: prop sphere gen}
could be solved by Riemannian optimization methods \cite{boumal2023introduction}
via the generalized $B^{\tT}B$-sphere.
Therefore,
we would relay on the tangent space of the (generalized) sphere $\bb S_D^{d-1}$ 
at some sphere point $v \in \bb S_D^{d-1}$ given by
\begin{equation*}
    \label{eq: tangent space}
    \bb T_{Dv} \coloneqq \ker(D h_C[v])
    = \{x \in \bb R^d \mid \scp{x}{D v} = 0\}
    = \spa\{Dv\}^\perp
    \quad \text{for} \quad
    v \in \bb S_D^{d-1},
\end{equation*}
where $h_D(v) \coloneqq \scp{v}{D v} - 1$
is the so-called local defining function. 
Hence $\bb S_D^{d-1} = h_D^{-1}(\{0\})$
is a smooth, embedded, $(d-1)$-dimensional Riemannian manifold.
Here, 
for solving \eqref{eq: prob sphere},
we relay on $D = I_d$ such that $\bb T_v = \{x \in \bb R^d \mid \scp{x}{v} = 0\} = \spa\{v\}^\perp$
for $v \in \bb S^{d-1}$.
The orthogonal projection onto the tangent space 
for the generalized sphere
is then defined by 
\begin{equation*}
    \label{eq: orth proj}
    P_{Dv} : \bb R^d \to \bb T_{Dv},
    \quad x \mapsto \Bigl(I_d - \frac{Dv (Dv)^{\tT}}{\norm{Dv}^2}\Bigr) x
    \quad \text{for} \quad
    v \in \bb S_D^{d-1},
\end{equation*}
and simplifies for \eqref{eq: prob sphere}
to $P_v (x) = (I_d - vv^{\tT}) x$ for $v \in \bb S^{d-1}$.
We further relay 
on the retraction 
at some sphere point $v \in \bb S_D^{d-1}$
defined by 
\begin{equation}
    \label{eq: retraction}
    R_{Dv} : \bb R^d \to \bb S_D^{d-1},
    \quad x \mapsto \frac{v + x}{\norm{v + x}_D^2}.
\end{equation}
and simplifies to $R_{Dv}(x) = \nicefrac{v + x}{\sqrt{1 + \norm{x}_D^2}}$ 
if $x \in \bb T_{Dv}$.
For solving
the optimization problem \eqref{eq: prob sphere},
two possible iterative approaches are
Riemannian first-order 
and zeroth-order Riemannian ascent methods.
We roughly outline them in the following.

\subsubsection{First-Order Riemannian Ascent Methods}
\label{sec: first order}

The general construction 
of first-order Riemannian gradient ascent methods \cite{boumal2023introduction}
for solving \eqref{eq: prob sphere}
utilizes the so-called Riemannain gradient 
of 
\eqref{eq: obj}
given by 
\begin{equation}
    \label{eq: riemannian gradient}
    \grad f(v) 
    = P_v \circ \nabla f (v),
    \quad v \in \bb S^{d-1},
\end{equation}
where $\nabla f(v)$ denotes the Euclidean gradient and reads as 
\begin{equation}
    \label{eq: euclidean grad}
    \nabla f(v) = \frac{2}{\norm{B v}^4}\bigl(\norm{B v}^2 A^{\tT}A v - \norm{A v}^2 B^{\tT}B v\bigr).
\end{equation}
Plugging \eqref{eq: euclidean grad} into \eqref{eq: riemannian gradient} yields 
$\grad f(v) = \nabla f(v)$ 
since $\nabla f(v) \in \spa\{v\}^\perp = \ker(x \mapsto (I_d - vv^{\tT}) x)$
such that $vv^{\tT} \nabla f(v) = 0 \in \bb R^d$.
The iterative algorithm breaks down to 
Alg.~\ref{alg: first order} in §~\ref{sec: alg}.
The critical points of \eqref{eq: prob sphere}
are therefore given by 
\begin{align}
    \label{eq: eigen}
    0 = \grad f(v)
    &\quad \Leftrightarrow \quad 
    \norm{B v}^2 A^{\tT}A v = \norm{A v}^2 B^{\tT}B v 
    \quad \Leftrightarrow \quad 
    (B^{\tT}B)^{-1}A^{\tT}A v = \frac{\norm{A v}^2}{\norm{B v}^2} v \notag \\
    &\quad \Leftrightarrow \quad 
    (B^{\tT}B)^{-1/2}A^{\tT}A (B^{\tT}B)^{-1/2} w = \frac{\norm{A (B^{\tT}B)^{-1/2} w}^2}{\norm{w}^2} w,
\end{align}
by a change of variables $(B^{\tT}B)^{1/2} v = w$.
Hence, the critical points 
are the eigen vectors 
of $(B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2}$,
also known as generalized eigen vectors of $(A^{\tT}A, B^{\tT}B)$.
The generalized eigen spaces are defined by 
\begin{equation*}
    \label{eq: gen eigen space}
    G_\lambda \coloneqq \{v \in \bb R^d \setminus \{0\} \mid A^{\tT}A v = \lambda B^{\tT}B v\}
\end{equation*}
where $\lambda$ is a 
generalized eigen value given in the set of generalized eigen values 
\begin{align*}
    \spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2}) 
    &= \{\lambda \in \bb R \mid \exists v \in \bb S^{d-1} , A^{\tT}A v = \lambda B^{\tT}B v\} \\
    &= \{\lambda_1,...,\lambda_d\},
    \quad \lambda_1 \geq \lambda_2 \geq ... \geq \lambda_d,
\end{align*}
by the symmetry of $(B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2} \in \mc S^d$.
Therewith,
it is 
\begin{equation*}
    \eqref{eq: prob}^2
    = \eqref{eq: prob sphere} 
    = \lambda_1 
    = \max_{\lambda \in \spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2})} \lambda
    \quad \text{and} \quad 
    \arg\eqref{eq: prob} \cap \bb S^{d-1}
    = G_{\lambda_1} \cap \bb S^{d-1}.
\end{equation*}


\subsubsection{Zeroth-Order Riemannian Ascent Methods}
\label{sec: zeroth order}

To avoid the adjoints $A^{\tT}$ and $B^{\tT}$,
for calculating the Riemannian \eqref{eq: riemannian gradient}, i.e. Euclidean \eqref{eq: euclidean grad}, gradient 
due to \eqref{eq: riemannian gradient}~f.,
one might approximate the gradient 
with a so-called numerical gradient \cite{li2023stochastic}
given by 
\begin{equation}
    \label{eq: num grad}
    \widehat{\grad}_1 f(v) 
    \coloneqq \frac{f(R_v(\mu \tilde x)) + f(v)}{\mu} \tilde x,
    \quad \text{where} \quad 
    \tilde x = P_v x,
    \quad x \sim \mc N(0, I_d).
\end{equation}
Here, 
a positive scaling parameter $\mu > 0$ 
ensures the ascent direction.
The numerical gradient is an unbiased estimator 
of the Riemnnian gradient by construction,
meaning that 
\begin{equation*}
    \bb E_{x \sim \mc N(0, I_d)} [\widehat{\grad}_1 f(v)]
    = \frac{1}{\mu d} \grad f(v).
\end{equation*}
Therefore,
a variance reduction 
by taking $m$ iid. samples 
constructed as in \eqref{eq: num grad}
and the estimated mean, i.e. 
\begin{equation*}
    \label{eq: num grad red}
    \widehat{\grad}_m f(v)
    \coloneqq \frac{1}{m} \sum_{i = 1}^m \frac{f(R_v(\mu \tilde x_i)) - f(v)}{\mu} \tilde x_i,
    \quad \text{where} \quad 
    \tilde x_i \coloneqq P_v x_i,
    \quad x_i \overset{\text{iid.}}{\sim} \mc N(0, I_d),
\end{equation*}
reduces the trace of the covariance matrix of $\widehat{\grad}_m$
in order $\mc O(\tfrac{1}{m})$.
More precisely holds 
\begin{equation*}
    \trace(\bb C\text{ov}[\widehat{\grad}_m f(v)]) 
    = \bb E\bigl[\norm{\bb E[\widehat{\grad}_m f(v)] - \widehat{\grad}_m f(v)}^2\bigr]
    \in \mc O (\tfrac{1}{m}).
\end{equation*}
The resulting ascent method is enrolled as in Alg.~\ref{alg: zeroth order}, cf.~§~\ref{sec: alg}.


\subsubsection{Second-Order Riemannian Ascent Methods}
\label{sec: second order}

For capturing even more information concerning the curvature of the considered objective,
one might use the Hessian and Riemannian Hessian.
Here, for the function of interest $f$, cf.~\eqref{eq: obj},
we have 
\begin{align}
    \label{eq: hess special}
    \nabla^2 f(v) = \tfrac{2}{\norm{B v}^2}\Bigl[
        &(A^{\tT}A - f(v) B^{\tT}B) 
        - \tfrac{2}{\norm{B v}^2}\bigl[(A^{\tT}A v)(B^{\tT}B v)^{\tT} + (B^{\tT}B v)(A^{\tT}A v)^{\tT}\bigr] \notag \\
        &\quad+ \tfrac{4}{\norm{B v}^4} (B^{\tT}B v)(B^{\tT}B v)^{\tT}
    \Bigr],
    \qquad v \in \bb R^d,
\end{align}
for the (Euclidean) Hessian 
and the Riemannian Hessian 
is given \cite{boumal2023introduction} by 
\begin{equation}
    \label{eq: riemannian hess}
    \hess f(v) = P_v \circ \nabla^2 f(v) \circ P_v,
    \qquad v \in \bb S^{d-1}.
\end{equation}
Therefore, plugging in \eqref{eq: hess special},
we obtain the simplification of \eqref{eq: riemannian hess} for \eqref{eq: obj} as
\begin{equation}
    \label{eq: riemannian hess special}
    \hess f(v) = \tfrac{1}{\norm{B v}^2} P_v (\underbracket{A^{\tT}A - f(v) B^{\tT}B}_{=:\,H(v)\,\in\,\mc S^d}) P_v,
    \qquad v \in \bb S^{d-1},
\end{equation}
since all remaining terms are in $\spa\{v\}$ 
and therefore in the kernel of $P_v$ 
so that the products with those terms vanish. 
We denote by $H(v)$
the inducing matrix of \eqref{eq: riemannian hess special}.


\subsection{Properties of the Objective}
\label{sec: prop obj}

In this subsection 
we summarize some properties of the considered (squared) objective \eqref{eq: obj}
for the optimization problem \eqref{eq: prob sphere}, respectively \eqref{eq: prob}.

\begin{lemma}
    \label{lem: lipschitz func}
    The objective \eqref{eq: obj} 
    is \smash{$\tfrac{2\norm{A}^2}{\lambda_d(B^{\tT}B)}(1 + \norm{B}^2)$}-Lipschitz continuous 
    on 
    $\bb S^{d-1}$.
\end{lemma}
\begin{proof} 
    It holds 
    \begin{align*}
        |f(v) - f(w)|
        & = \left|\tfrac{\scp{v}{A^{\tT}A v}}{\scp{v}{B^{\tT}B v}} - \tfrac{\scp{w}{A^{\tT}A w}}{\scp{w}{B^{\tT}B w}}\right| \\
        & = \tfrac{|\scp{v}{A^{\tT}A v} - \scp{w}{A^{\tT}A w}|}{|\scp{v}{B^{\tT}B v}|} 
        + |\langle w, A^{\tT}A w\rangle|\cdot\left|\tfrac{1}{\scp{v}{B^{\tT}B v} - \scp{w}{B^{\tT}B w}} \right| \\
        & \leq 2 \bigl(\tfrac{\|A\|^2}{\lambda_{d}(B^{\tT}B)} 
        + \tfrac{\|A\|^2\|B\|^2}{\lambda_{d}(B^{\tT}B)^2}\bigr)\|v - w\|,
        \qquad\qquad v, w \in \bb S^{d-1}.
        \tag*{\qedhere}
    \end{align*}
\end{proof}

\begin{lemma}
    \label{lem: lipschitz grad}
    The (extended) gradient 
    of the objective \eqref{eq: obj} 
    is \smash{$\tfrac{20}{\lambda_{d}(B^{\tT}B)^4} \|A\|^2\|B\|^6$}-Lipschitz continuous 
    on 
    $\bb S^{d-1}$. 
\end{lemma}
\begin{proof}
    See §~\ref{sec: app}.
\end{proof}

\section{General Construction}

In \cite{B9,B8},
a random step direction for a current iterate $v^k$, 
i.e. a surrogate of the Riemannian gradient, is constructed
in each iteration $k \in \bb N$
in $\bb T_{v^k} \cap \bb S^{d-1}$.
More precisely, it is proposed \cite[Rem.~4.1]{B9} to take 
\begin{equation}
    \label{eq: tangent surrogate}
    x^k \coloneqq \frac{P_{B^{\tT}Bv^k} x^k}{\norm{P_{B^{\tT}Bv^k} x^k}} 
    \sim \bb P_{X^k \mid V^k = v^k} = \mc U (\bb T_{B^{\tT}B v^k} \cap \bb S^{d-1})
\end{equation}
with $x^k \coloneqq \frac{x}{\norm{x}}$, where $x \sim \mc N(0, I_d)$.
This is motivated by the property of the Riemannian gradient,
cf. \eqref{eq: riemannian gradient}~f.,
and the fact that \eqref{eq: tangent surrogate} is an unbiased estimator
of the (true) Riemannian gradient \cite[Lem.~4.1]{B9} for solving \eqref{eq: prop sphere gen},
i.e. it holds w.r.t. \eqref{eq: tangent surrogate} that
\begin{equation}
    \label{eq: connection grad length}
    \bb E_{x^k \sim X^k \mid V^k = v^k}[\scp{A^{\tT}A v^k}{x^k}x^k] 
    = \frac{2}{d} P_{B^{\tT}B v^k} A^{\tT}A v^k 
    = \frac{2}{d} \grad \norm{A v^k}^2.
\end{equation}
Here, 
since we are not aware of $B^{\tT}B$
and, hence, working on the generalized sphere \cite{B9} is not possible,
we propose a more general 
and unconstrained sampling approach.
More precisely, we chose $x^k \sim \mc U(\bb S^{d-1})$
uniformly distributed on the entire unit sphere \cite[Ex. 3.3.7]{vershynin2018highdimprob}
given by 
\begin{equation}
    \label{eq: x^k}
    x^k \coloneqq \frac{x}{\norm{x}^2},
    \qquad x \sim \mc N(0, I_d)
\end{equation}
with property
$\bb E_{x \sim \mc N(0, I_d)}[x^k(x^k)^{\tT}] = \bb E_{x^k \sim \mc U(\bb S^{d-1})}[x^k(x^k)^{\tT}] = \tfrac{1}{d} I_d$.
Therefore, 
we resolved the issue 
for discussing conditional distributions
as we have $\bb P_{X^k \mid V^k=\cdot} = \bb P_{X^k} = \mc U(\bb S^{d-1})$,
which is necessary for the construction in \cite{B9,B8}, cf.~\eqref{eq: tangent surrogate}.
Afterwards,
we aim to solve the following optimal step size problem 
in each iteration $k \in \bb N$
given by 
\begin{equation}
    \label{eq: sub prob}
    \tau_k \in \argmax_{\tau \in \bb R} s_k(\tau)
    \quad \text{where} \quad 
    s_k (\tau)
    \coloneqq 
    f(R_{v^k}(\tau x^k)),
\end{equation}
which simplifies to a quotient of quadratic functions 
\begin{equation}
    \label{eq: sub prob func}
    s_k(\tau)
    = f(v^k + \tau x^k)
    = \frac{\norm{A(v^k + \tau x^k)}^2}{\norm{B(v^k + \tau x^k)}^2}
    = \frac{a_k + b_k \tau + c_k \tau^2}{d_k + e_k \tau + f_k \tau^2},
\end{equation}
where 
\begin{equation}
    \label{eq: para mgRq}
    \begin{array}{c c c}
        a_k \coloneqq \norm{A v^k}^2, 
        & b_k \coloneqq \scp{A v^k}{A x^k}, 
        & c_k \coloneqq \norm{A x^k}^2, \\
        d_k \coloneqq \norm{B v^k}^2, 
        & e_k \coloneqq \scp{B v^k}{B x^k}, 
        & f_k \coloneqq \norm{B x^k}^2.
    \end{array}
\end{equation}
The proposed algorithm is summarized in Alg.~\ref{alg: main}.
Notably,
the construction 
via the tangent spaces in \cite{B9,B8}, cf.~\eqref{eq: tangent surrogate},
allow for a much simpler quotient in \eqref{eq: sub prob func},
where the denominator reduces to $\tau \mapsto 1 + f_k \tau^2$, cf.~\eqref{eq: retraction}~f.,
and $f_k > 0$.
Now,
the analysis for solving \eqref{eq: sub prob}
involves even more theoretical background 
than just calculating the roots of
\begin{align}
    \label{eq: sub prob stationary}
    s_k'(\tau)
    & = \frac{b_kd_k - a_ke_k
        + \tau (c_kd_k - a_kf_k) 
        + \tau^2 (c_ke_k - b_kf_k)}{(d_k + 2 \tau e_k + \tau^2 f_k)^2}.
\end{align}
Note that 
$d_k = \norm{v^k}_{B^{\tT}B}^2 \geq \lambda_d(B^{\tT}B) > 0$ 
and for any $\tau \in \bb R \setminus\{0\}$ as longs as $x^k \not \in \spa\{v^k\}$ holds
$d_k + 2 \tau e_k + \tau^2 f_k = \norm{v^k + \tau x^k}^2_{B^{\tT}B}$ and 
\begin{equation}
    \label{eq: sum d e f}
    \norm{v^k + \tau x^k}^2_{B^{\tT}B} 
    \leq \lambda_d(B^{\tT}B) \norm{v^k + \tau x^k}^2
    \geq 2 \lambda_d(B^{\tT}B) (1 - \langle x^k, v^k\rangle^2)
    > 0.
\end{equation}
\newpage

\begin{algorithm}[H]
    \caption{Unconstrained zeroth-order Riemannian gradient ascent method}
    \label{alg: main}
    \begin{algorithmic}
        \State{\textbf{Given} $A \in \bb R^{m \times d}$ and $B \in \bb R^{\ell \times d}$ such that $\rank(B) = d$.}
        \State{\textbf{Initialize} with $v^0 \in \bb S^{d-1}$ for instance $v^0 = \tfrac{x}{\norm{x}}$ for $x \sim \mc N(0, I_d)$.}
        \For{$k = 1,2,3,...$}
        \State{\textbf{Sample} $x^k = \tfrac{x}{\norm{x}}$ via $x \sim \mc N(0, I_d)$ as in \eqref{eq: x^k}.}
        \State{\textbf{Calculate} $\tau_k$ according to \eqref{eq: sub prob} and
        \textbf{update} $v^{k+1} = R_{v^k}(\tau_k x^k) = \tfrac{v^k + \tau_k x^k}{\norm{v^k + \tau x^k}}$.}
        \EndFor
        \State{\textbf{Return} estimate $\norm{A/B} \approx \tfrac{\norm{A v^k}}{\norm{B v^k}} = \sqrt{\tfrac{a_k}{d_k}}$.}
    \end{algorithmic}
\end{algorithm}

\vspace{-15pt}

\begin{remark}[Connection to \cite{B8} and \cite{B9}]
    \label{rem: connection}
    All theoretical results are done for the case $C = A^{\tT}A$ and $D = B^{\tT}B$ for a direct connection to \cite{B8}
    as adjoint-free approach and connects to \cite{B9} for $\nicefrac{\scp{v}{C v}}{\scp{v}{D v}}$.
    However, all the novel, presented results remain true for general matrices $(C, D)$,
    where $D \in \mc S_+^d$ just has to be Hermitian, positive definite 
    such that $D^{1/2}$ exist with $D = D^{1/2}D^{1/2}$
    and we may have 
    \vspace{-3pt}
    \begin{equation*}
    \begin{array}{c c c}
        a_k \coloneqq \langle v^k, C v^k\rangle, 
        & b_k \coloneqq \langle v^k, C x^k\rangle, 
        & c_k \coloneqq \langle x^k, C x^k\rangle, \\
        d_k \coloneqq \langle v^k, D v^k\rangle, 
        & e_k \coloneqq \langle v^k, D x^k\rangle,
        & f_k \coloneqq \langle x^k, D x^k\rangle.
    \end{array}
\end{equation*}
\end{remark}


\begin{remark}[Distribution of $(v^k, x^k)_{k \in \bb N}$]
    \label{rem: dist x^k v^k}
    The generated sequence 
    of iterates $(v^k)_{k \in \bb N}$ from Alg.~\ref{alg: main}
    is a sequence of samples from a Markov chain $(V^k)_{k \in \bb N}$.
    Here, for each $k \in \bb N$ the law is given by $P_{V^k} \coloneqq (V^k)_{\#} \bb P = \bb P \circ (V^{k})^{-1}$
    on a probability space $(\Omega, \mf A, \bb P)$.
    As discussed \eqref{eq: x^k}~ff., 
    the step dirctions are samples from a random variable $X^k : \Omega \to \bb S^{d-1}$
    with law $\bb P_{X^k} = \mc U(\bb S^{d-1})$
    so that we deal with the surface measure $\sigma_{\bb S^{d-1}}$,
    which resolves the conditional properties from \cite[Rem.~4.1]{B9}.
    The iterates are samples from a conditional distribution \smash{$\bb P_{V^{k+1} \mid V^k}$},
    which defines the Markov kernel.
    Hence, \smash{$\bb P_{V^{k+1} \mid V^k=v^k}$} is a measure for each $v^k \in \bb S^{d-1}$
    and \smash{$\bb P_{V^{k+1} \mid V^k=\cdot}(A)$} is a measurable function 
    for any Borel set $A \in \mc B(\bb S^{d-1})$.
    Throughout the paper 
    we call an event almost surely (a.s.)
    if it happens with probability one,
    i.e. the counter event is with portability zero,
    with respect to $\bb P_{X^k}$.
\end{remark}


For the probabilistic proofs,
we relay on two theoretical results 
concerning the distribution 
of the random step directions, from Rem.~\ref{rem: dist x^k v^k}.
\begin{proposition}[{\cite[Lem.~4.2]{B9}}]
    \label{prop: measure zero affine space}
    Let $M \subset \bb R^d$ be an affine subspace of $\bb R^d$
    and 
    \vspace{-5pt}
    \begin{equation*}
        \varphi : M \setminus \{0\} \to \bb S^{d-1}, 
        \qquad x \mapsto \tfrac{x}{\norm{x}}.
        \vspace{-5pt}
    \end{equation*}
    Then, w.r.t. $\mc U(\bb S^{d-1})$ the uniform distribution on $\bb S^{d-1}$, holds
    \begin{enumerate}
        \vspace{-7pt}
        \item[i)] $\varphi(M)$ is a measure zero set if $0 \in M$ and $\dim(M) < d$,
        \vspace{-7pt}
        \item[ii)] $\varphi(M)$ is a measure zero set if $0 \not\in M$ and $\dim(M) < d-1$.
    \end{enumerate}
\end{proposition}


\begin{proposition}[{\cite[Thm.~A.4]{langrenez2024setkirkwooddiracpositivestates},\cite{mityagin2020measurezero}}]
    \label{prop: measure zero roots}
    Let $\varrho : \bb R^{d} \to \bb R$ be a polynomial.
    Then the set 
    \vspace{-5pt}
    \begin{equation*}
        \varrho^{-1}(\{0\}) \cap \bb S^{d-1} = \{x \in \bb S^{d-1} : \varrho(x) = 0 \}
        \vspace{-8pt}
    \end{equation*} 
    is either 
    \begin{enumerate}
        \vspace{-7pt}
        \item[i)] a null set w.r.t. $\mc U(\bb S^{d-1})$ the uniform distribution on $\bb S^{d-1}$,
        or 
        \vspace{-7pt}
        \item[ii)] the entire sphere $\bb S^{d-1}$, i.e. $\varrho \equiv 0$ on $\bb S^{d-1}$.
    \end{enumerate} 
\end{proposition}


\begin{remark}[Well-definiteness of the update scheme]
    \label{rem: norm not zero}
    For a well defined next iterate $v^{k+1}$,
    we have to ensure 
    that the denominator, i.e. the norm of $v^k + \tau x^k$,
    is not zero, to have, 
    even without normalization 
    for the retraction \eqref{eq: retraction},
    a well defined objective value, cf.~\eqref{eq: sum d e f}~f.
    Therefore,
    we observe that $\norm{v^k + \tau x^k} = 0$ 
    for some $\tau \in \bb R$ holds 
    if and only if
    \begin{equation*}
        x^k \in \spa\{v^k\}
        \quad \text{with} \quad
        \bb P_{X^k}(x^k \in \{v^k,-v^k\}) 
        = 0,
    \end{equation*}
    using Prop.~\ref{prop: measure zero affine space}~i), 
    since $0 \in \spa\{v^k\}$ is an one-dimensional subspace in $\bb R^d$.
\end{remark}


\subsection{Well-definiteness of the Sequence}

Differently to \cite{B8,B12,B9}
where the existence of the unique maximizer is clear under certain constructions, 
cf.~\eqref{eq: retraction} and \eqref{eq: sub prob func}~f.,
the existence and well-definiteness for \eqref{eq: sub prob} 
is shown by reformulating the problem 
to an equivalent extremal generalized Rayleigh quotient problem
for ($2\times2$)-matrices.

\begin{theorem}
    \label{thm: svd}
    The problem \eqref{eq: sub prob} 
    is equivalent to the extremal generalized eigenvector problem
    for 
    $$
        M_k \coloneqq \left[\begin{smallmatrix}
            a_k & b_k \\ b_k & c_k
        \end{smallmatrix}\right],
    \qquad 
    N_k \coloneqq \left[\begin{smallmatrix}
            d_k & e_k \\ e_k & f_k
        \end{smallmatrix}\right],
    $$
    if $N_k \succ 0$ and $a_k, b_k, c_k$, and $d_k$ are given as in \eqref{eq: para mgRq}.
    Furthermore, \eqref{eq: sub prob} is well-defined
    and solved by 
    \begin{equation*}
        \label{eq: opt tau}
        \tau_k = -\tfrac{\beta_k}{2\gamma_k} + \sign(\alpha_k/\gamma_k) \sqrt{\tfrac{\beta_k^2}{4\gamma_k^2} - \tfrac{\alpha_k}{\gamma_k}},
        \qquad \textrm{where} \qquad 
        \left\{\begin{array}{r l}
            \alpha_k &\coloneqq  b_kd_k - a_ke_k, \\
            \beta_k  &\coloneqq c_kd_k - a_kf_k, \\
            \gamma_k &\coloneqq c_ke_k - b_kf_k,
        \end{array}\right.
    \end{equation*}
    whenever $\gamma_k \neq 0$.
\end{theorem}
\begin{proof}
    Firstly,
    we show the closed form solution,
    which might be sofar not reel-valued:
    The stationary condition for \eqref{eq: sub prob} is given in \eqref{eq: sub prob stationary}.
    Hence, the last assertion follows immediately
    if $\gamma_k \neq 0$ due to
    \begin{equation*}
        0 = s_k'(\tau)
        \quad \Leftrightarrow \quad 
        0 = \tfrac{\alpha_k}{\gamma_k} + \tau \tfrac{\beta_k}{\gamma_k} + \tau^2
        \quad \Leftrightarrow \quad 
        \tau^\pm = - \tfrac{\beta_k}{2\gamma_k} \pm \sqrt{\tfrac{\beta_k^2}{4\gamma^2_k} - \tfrac{\alpha_k}{\gamma_k}}.
    \end{equation*}
    Taking $\tau = 0$ into account 
    yields $s_k'(0) = 2(b_kd_k - d_ke_k)/d_k^2 = 2 \alpha_k/d_k^2$.
    Therewith, 
    the forsign of the square-root,
    i.e. the maximizer, 
    is given by $\sign(s_k'(0)/\gamma_k) = \sign(\alpha_k/\gamma_k)$,
    since $d_k > 0$ by construction, i.e. because of $\ker(B) = \{0\}$,
    or equivalently $B^{\tT}B \succ 0$,
      
    Secondly, we discuss the reel-valued property 
    of the solution, i.e. the non-negativity of the argument of the square-root:
    The Gram matrices $M_k, N_k \in \bb R^{2\times 2}$ 
    are equivalently given by 
    \begin{align*}
        M_k & \coloneqq [v^k, x^k]^{\tT} A^{\tT}A [v^k, x^k]
        = \left[\begin{smallmatrix}
            \scp{u^k}{u^k} & \scp{u^k}{w^k} \\ \scp{u^k}{w^k} & \scp{w^k}{w^k}
        \end{smallmatrix}\right]
        = [u^k, w^k]^{\tT} [u^k, w^k]
    \end{align*}
    and
    \begin{align*}
        N_k & \coloneqq [v^k, x^k]^{\tT} B^{\tT}B [v^k, x^k]
        = \left[\begin{smallmatrix}
            \scp{y^k}{y^k} & \scp{y^k}{z^k} \\ \scp{y^k}{z^k} & \scp{z^k}{z^k}
        \end{smallmatrix}\right]
        = [y^k, z^k]^{\tT} [y^k, z^k],
    \end{align*}
    where 
    \begin{equation}
        \label{eq: y z}
        u^k \coloneqq A v^k,
        \quad w^k \coloneqq A x^k,
        \quad y^k \coloneqq B v^k,
        \quad \text{and} \quad 
        z^k \coloneqq B x^k.
    \end{equation}
    Recall, for Gram matrices 
    does hold $M_k, N_k \succeq 0$, always.
    If $N_k \succ 0$, then the stationary condition $s_k'(\tau) = 0$ from \eqref{eq: sub prob stationary}
    is equivalent to the 2d generalized Rayleigh quotient problem 
    given by 
    \begin{equation}
        \label{eq: small}
        M_k \xi(\tau) = \eta N_k \xi(\tau), 
        \qquad \text{with} \qquad 
        \xi(\tau) = \left[\begin{smallmatrix}
            \tau \\ 1
        \end{smallmatrix}\right]
        \qquad \text{and optimal} \qquad \eta, \tau \in \bb R, 
    \end{equation}
    since the generalized Rayleigh quotient then satisfies
    \begin{equation}
        \label{eq: sub prob equiv}
        \frac{\scp{\xi(\tau)}{M_k \xi(\tau)}}{\scp{\xi(\tau)}{N_k \xi(\tau)}}
        = \frac{a_k + \tau b_k + \tau^2 c_k}{d_k + \tau e_k + \tau^2 f_k} = s_k(\tau).
    \end{equation}
    Hence,
    the solutions in $\eta$ of \eqref{eq: small} 
    and by \eqref{eq: sub prob equiv}
    for \eqref{eq: sub prob}
    are real, whenever $N_k$ is positive definite.
\end{proof}

Notably,
the property $\gamma_k \neq 0$ ensures that $\tau \to \pm \infty$
does not maximizes \eqref{eq: sub prob equiv} and hence \eqref{eq: sub prob}
so that the update scheme is well-defined under the assumption of Thm.~\ref{thm: svd}.

\begin{remark}[Sub-SVD problem for \cite{B9}]
    Considering the extremal generalized Raleigh quotient problem $\mc R(C, D)$ from \eqref{eq: obj}~ff. \cite{B9},
    then the optimal step size problem 
    reads as sub-SVD problem w.r.t.
    \begin{equation*}
        M_k \coloneqq \left[\begin{smallmatrix}
            a_k & \nicefrac{b_k}{2} \\ \nicefrac{b_k}{2} & c_k
        \end{smallmatrix}\right]
        \quad \text{and} \quad 
        N_k \coloneqq \diag(1, f_k) \succ 0,
    \end{equation*}
    since $d_k = 1$ and $e_k = 0$
    by construction due to $v^k \in \bb S_D^{d-1}$
    and $x^k \in \bb T_{Dv^k}$, cf.~Rem.~\ref{rem: connection}.
\end{remark}

For ensuring that $N_k \succ 0$ from Thm.~\ref{thm: svd},
and translating the property to properties of $\{v^k, x^k\}_{k \in \bb N}$,
recall that $N_k \succ 0$,
if any only if $y^k$ and $z^k$ are linear independent,
which means by \eqref{eq: y z} that $v^k$ and $x^k$ are $B$-linear independent.

\begin{lemma}
    \label{lem: N_k pos def}
    If $\ker(B) = \{0\}$, 
    then $v^k$ and $x^k$ are $B$-linear independent a.s.,
    hence $y^k$ and $z^k$ are linear independent a.s.,
    and $N_k \succ 0$ a.s.
\end{lemma}
\begin{proof}
    Let $v^k \in \bb S^{d-1}$, and notice that $B v^k \neq 0$ as well as $B^{\tT}B v^k$.
    To show that $x^k$ and $v^k$ are not $B$-colinear,
    i.e. $y^k$ and $z^k$ are not colinear and hence linear independent such that $N^k \succ 0$ (a.s.),
    the contrary is assumed.
    To this end, let $\lambda \in \bb R\setminus\{0\}$ exists such that 
    \begin{equation*}
        \lambda y^k = z^k 
        \quad\Leftrightarrow\quad 
        \lambda B v^k = B x^k
        \quad\Rightarrow\quad
        \lambda B^{\tT}B v^k = B^{\tT}B x^k
        \quad\Leftrightarrow\quad 
        \lambda v^k = x^k
    \end{equation*}
    under the assumption that $\ker(B) = \{0\}$ 
    i.e. $B^{\tT} B \succ 0$,
    and hence $(B^{\tT} B)^{-1}$ exists.
    By construction,
    we then have $1 = \norm{x^k} = \norm{\lambda v^k} = |\lambda| \cdot \norm{v^k} = |\lambda|$
    and hence $x^k \in \{v^k, - v^k\} = \spa\{v^k\} \cap \bb S^{d-1}$.
    Similar to the argument in Rem.~\ref{rem: norm not zero},
    we obtain by Prop.~\ref{prop: measure zero affine space}~i) that
    \begin{equation*}
        \bb P_{X^k}(x^k \in \spa\{v^k\} \cap \bb S^{d-1})
        = \bb P_{X^k}(x^k \in \{v^k, -v^k\})
        = 0,
    \end{equation*}
    which yields the assertion.
\end{proof}


Next,
the first case $\gamma_k = 0$ is studied,
where $\gamma_k \neq 0$ would ensure under $N_k \succ 0$
the closed form for the optimal step sizes, see Thm.~\ref{thm: svd} and Lem.~\ref{lem: N_k pos def}.
The second case $\alpha_k = 0$ detects a generalized eigen pair
given by $(v^k, \nicefrac{\norm{A v^k}^2}{\norm{B v^k}^2})$.
Therefore,
we translate the problem to properties of the random variables $v^k \in \bb S^{d-1}$.
In the following, we always assume that $\ker(B) = \{0\}$.
Here, we mainly utilize Prop.~\ref{prop: measure zero roots}.


\begin{lemma}
    \label{lem: gamma_k}
    Let $v^k \in \bb S^{d-1}$ be not a generalized eigenvector of $(A^{\tT}A, B^{\tT}B)$.
    If $x^k$ is sampled as in \eqref{eq: x^k},
    then $\gamma_k \neq 0$ 
    and $\alpha_k \neq 0$ a.s.
\end{lemma}
\begin{proof}
    For the first assertion
    assume the contrary $\gamma_k = 0$
    and observe 
    \begin{align*}
    0 &= \gamma_k = \scp{x^k}{A^{\tT}Ax^k}\scp{B^{\tT}Bx^k}{v^k} - \scp{x^k}{B^{\tT}Bx^k}\scp{A^{\tT}Ax^k}{v^k} \notag \\
    \Leftrightarrow \quad 
    0 &= \scp{x^k}{\Bigl(\tfrac{\scp{x^k}{A^{\tT}Ax^k}}{\scp{x^k}{B^{\tT}Bx^k}} B^{\tT}B - A^{\tT}A\Bigr)v^k}.
    \label{eq:gamma_k}
    \end{align*}
    To this end, 
    define the cubic function $\gamma(x)$ in terms of Prop.~\ref{prop: measure zero roots}
    \begin{equation*}
        \gamma(x) \coloneqq \scp{x}{A^{\tT}Ax}\scp{B^{\tT}Bx}{v^k} - \scp{x}{B^{\tT}Bx}\scp{A^{\tT}Ax}{v^k}.
    \end{equation*}
    Then, by Prop.~\ref{prop: measure zero roots}
    the set of roots on the sphere are either measure zero 
    w.r.t. uniform distribution 
    or $\gamma \equiv 0$.
    Therefore, 
    let $B^{\tT}B = \tilde B^{1/2} \tilde B^{1/2}$ due to the Hermitian, positive definiteness, 
    and define 
    \begin{equation}    
        \label{eq: para alpha beta}
        y \coloneqq \tilde B^{1/2}x, \quad \tilde A \coloneqq \tilde B^{-1/2} A^{\tT}A \tilde B^{-1/2},
        \quad a^k \coloneqq \tilde B^{-1/2} A^{\tT}A v^k, \quad b^k \coloneqq  \tilde B^{1/2}v^k,
    \end{equation}
    such that
    \begin{equation*}
        \gamma(y) = \scp{y}{\tilde A y} \scp{y}{a^k} - \norm{y}^2 \scp{y}{b^k}.
    \end{equation*}
    On $\bb T_{a^k}\setminus\{0\}$, it holds $\gamma(y) = - \norm{y}^2 \langle y, b^k\rangle$.
    Under contrary assumption in Prop.~\ref{prop: measure zero roots}, 
    we then have $0 = \norm{y}^2 \langle y, b^k\rangle$ on $\bb T_{a^k}\setminus\{0\}$.
    Since $\norm{y} \neq 0$,
    it necessary holds $\langle y, b^k\rangle = 0$ on $\bb T_{a^k}\setminus\{0\}$.
    Furthermore this holds for any $y \in \bb T_{a^k}$,
    hence $a^k$ and $b^k$ are colinear,
    i.e. there exists $\lambda \in \bb R\setminus\{0\}$,
    such that 
    \begin{align*}
        \lambda a^k = b^k 
        \quad \Leftrightarrow \quad 
        \lambda \tilde B^{-1/2} A^{\tT}A v^k = \tilde B^{1/2} v^k 
        \quad \Leftrightarrow \quad 
        \lambda A^{\tT}A v^k = B^{\tT}B v^k.
    \end{align*}
    In turn, this implies
    that $v^k$ is a generalized eigenvector of $(A^{\tT}A, B^{\tT}B)$
    and contradicts the assumption.
    This yields the first assertion.
    %
    For the second assertion, observe similarly that 
    \begin{align*}
        0 &= \alpha_k = \scp{v^k}{A^{\tT}Ax^k}\scp{B^{\tT}Bv^k}{v^k} - \scp{v^k}{B^{\tT}Bx^k}\scp{A^{\tT}Av^k}{v^k} \notag \\
        \Leftrightarrow \quad 
        0 &= \scp{x^k}{\Bigl(\tfrac{\scp{v^k}{A^{\tT}Av^k}}{\scp{v^k}{B^{\tT}Bv^k}} B^{\tT}B - A^{\tT}A\Bigr)v^k}.
    \end{align*}
    To this end,
    define the cubic function in terms of Prop.~\ref{prop: measure zero roots}
    \begin{equation*}
        \alpha(x) \coloneqq \scp{v^k}{A^{\tT}Ax}\scp{B^{\tT}Bv^k}{v^k} - \scp{v^k}{B^{\tT}Bx}\scp{A^{\tT}Av^k}{v^k}
    \end{equation*}
    and substituting with the parameters from \eqref{eq: para alpha beta}
    yields 
    \begin{equation*}
        \alpha(y) = \scp{b^k}{\tilde A y} \norm{b^k}^2 - \scp{y}{b^k} \scp{a^k}{b^k}.
    \end{equation*}
    Again, 
    on $\bb T_{b^k}\setminus\{0\}$, 
    one obtains $\alpha(y) = \langle b^k, \tilde A y\rangle \norm{b^k}^2$
    and by taking the contrary to Prop.~\ref{prop: measure zero roots} in account, 
    it holds $0 = \langle b^k,\tilde A y\rangle$,
    since $\norm{b^k}^2 \neq 0$.
    By the symmetry of $\tilde A$
    and since $0 = \langle \tilde A b^k,y\rangle = 0$ for all $y \in \bb T_{b^k}$,
    the colinearity of $b^k$ and $\tilde A b^k$ follows.
    Hence,
    there exists some $\lambda \in \bb R \setminus\{0\}$ such that
    \begin{equation*}
        \lambda \tilde A b^k = b^k
        \quad\Leftrightarrow \quad 
        \lambda \tilde B^{-1/2}A^{\tT}A \underbracket{\tilde B^{-1/2} \tilde B^{1/2}}_{= I_d} v^k = \tilde B^{1/2} v^k
        \quad\Leftrightarrow\quad 
        \lambda A^{\tT}A v^k = B^{\tT}B v^k,
    \end{equation*}
    yielding a generalized eigenvector $v^k$ of $(A^{\tT}A, B^{\tT}B)$,
    contradicting the assumption, again.
\end{proof}



\subsection{Relation to Generalized Eigenspaces}
\label{sec: gen eigenspaces}

In this section,
we translated the non generalized eigenvector condition of the iterates $v^k$
to an assumption on the size of the spectrum of $(B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2}$.


\begin{proposition}
    \label{prop: update}
    If $\# \spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2}) > 1$,
    then 
    \begin{enumerate}[label=\roman*)]
        \item $v^0 = \tfrac{\hat v}{\norm{\hat v}}$, 
        where $\hat v \sim \mc N(0,I_d)$, is not a generalized eigenvector a.s.,
        \item if $\dim(G_{\lambda_1}) = d-1$,
        then $v^1 \in G_{\lambda_1}$ is a leading generalized eigenvector a.s.,
        \item if $\dim(G_\lambda) < d-1$ 
        and $v^k \not \in G_\lambda$, 
        then $v^{k+1} \not\in G_\lambda$ a.s.
    \end{enumerate}
    If $\# \spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2}) = 1$,
    then $v^0 \in G_{\lambda_1}$ is a generalized eigenvector a.s.
\end{proposition}

The latter proposition 
claims that the proposed method converges 
either after zero or one iteration 
(the convergence after finitely many iterations)
or proceeds, inductively,  for $k \to \infty$
by Lem.~\ref{lem: gamma_k}.
For proving Prop.~\ref{prop: update},
the next lemma discusses the dimension of the projected sets of search directions
as affine subspaces.

\begin{lemma}
    \label{lem: set directions}
    Let $v \in \bb S^{d-1}$ be no generalized eigenvector of $(A^{\tT}A, B^{\tT}B)$,
    i.e. it holds $v \not\in G_\lambda$ 
    for any $\lambda \in \spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2})$.
    Then 
    \begin{equation*}
        S_{v,\lambda} \coloneqq \{x \in \bb R^d \mid v + x \in G_\lambda\} \not\ni 0
    \end{equation*}
    is an affine space and has dimension $\dim(G_\lambda)$.
\end{lemma}
\begin{proof}
    Recall that the set $S_{v,\lambda}$ can be rewritten in the following manner:
    \begin{equation*}
        x \in S_{v,\lambda} \quad \Leftrightarrow \quad 
        \exists u \in G_\lambda : v + x = u
        \quad \Leftrightarrow \quad 
        x \in (-v) + G_\lambda.
    \end{equation*}
    This directly provides by the dimension of $G_\lambda$ the dimension of $S_{v,\lambda}$.
    Assume $0 \in S_{v,\lambda}$, this implies $v \in G_\lambda$,
    and contradicts the assumption; 
    this finishes the proof.
\end{proof}

Now Prop.~\ref{prop: measure zero affine space}
i.e.~\cite[Prop.~6.5 \& Cor.~6.12]{Lee2012smoothmanifolds},
can be utilized 
on the finite union of the sets $S_{v,\lambda}$ 
for all $\lambda \in \spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2})$
and one fixed $v \in \bb S^{d-1}$.
Therefore,
we consider the union of finitely many generalized eigen spaces
\begin{equation*}
    \label{eq: all gen eigen spaces}
    G \coloneq \bigcup_{\lambda \in \spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2})} G_\lambda
\end{equation*}

\begin{proof}[Proof of Prop.~\ref{prop: update}]
    Assume, firstly, $\# \spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2}) > 1$:
    For part i). 
    By Prop.~\ref{prop: measure zero affine space}~i),
    the sets 
    $\{\nicefrac{x}{\norm{x}} \cap G_\lambda : x \in \bb R^d\setminus\{0\}\} = \varphi(G_\lambda \setminus \{0\}\}$
    are of measure zero with respect to $\mc U(\bb S^{d-1})$ the uniform distribution 
    since $0 \in G_\lambda$ and $\dim(G_\lambda) \leq d-1 < d$
    according to the construction of $v^0$, i.e. $\bb P_{V^0} = \mc U(\bb S^{d-1})$.
    Hence,
    we have
    \begin{equation}
        \label{eq: prop V^0}
        \bb P_{V^0}(v^0 \in G_\lambda) = 0
        \quad \text{such that} \quad 
        \bb P_{V^0}(v^0 \in G) = 0
    \end{equation}
    by the $\sigma$-subadditivity of the probability measure.
    %
    For part ii). By i) follows that $v^0$ is not a generalized eigenvector a.s., 
    i.e. with $v^0 \not\in G$ it holds 
    $$
        \lambda_1
        \geq \nicefrac{\scp{A^{\tT}A v^1}{v^1}}{\scp{B^{\tT}B v^1}{v^1}} 
        < \nicefrac{\scp{A^{\tT}A v^0}{v^0}}{\scp{B^{\tT}B v^0}{v^0}} 
        > \lambda_2,
        \qquad \text{a.s}.
    $$
    Moreover, by Lem.~\ref{lem: set directions}, 
    it holds $\dim(S_{v^0,\lambda_1}) = \dim(G_{\lambda_1}) = d-1$ a.s.
    Since $v^0 \not\in G_{\lambda_1} \cap \bb S^{d-1}$,
    especially $v^0$ is linear independent to any basis of $G_{\lambda_1}$ a.s.,
    there is an orthonormal basis $\{u_j\}_{j = 1}^{d-1}$ of $G_{\lambda_1}$ such that $\{v^0, u_1,..., u_{d-1}\}$
    is a basis of $\bb R^d$.
    Now, consider 
    \begin{equation*}
        x \in S_{v^0, \lambda_1} 
        \quad \Leftrightarrow\quad 
        v^0 + x \in G_{\lambda_1}
        \quad \Leftrightarrow\quad 
        x = -\eta_0 v^0 + \sum_{j = 1}^{d-1} \eta_j u_j
    \end{equation*}
    for some $\{\eta_j\}_{j = 0}^{d-1} \in \bb R$.
    This construction follows visa versa
    such that 
    with $\bb P_{X^1} = \mc U(\bb S^{d-1})$, cf.~Rem.~\ref{rem: dist x^k v^k},
    holds
    \begin{equation*}
        \bb P_{V^1 \mid V^0 = v^0}(v^1 \in G_{\lambda_1})
        = \bb P_{X^1}(x^1 \in S_{v^0, \lambda_1})
        = 1,
        \qquad v^0 \not \in G
    \end{equation*}
    By the law of total probability and with \eqref{eq: prop V^0} holds
    \begin{equation*}
        \bb P_{V^1}(v^1 \in G_{\lambda_1})
        = \int_{\bb S^{d-1} \setminus G}
        \bb P_{V^1 \mid V^0 = v^0}(v^1 \in G_{\lambda_1})
        \; \mathrm{d} \bb P_{V^0}(v^0)
        = \bb P_{V^0}(v^0 \not\in G)
        = 1
    \end{equation*}
    and the assertion follows.
    %
    For part iii). First, by Lem.~\ref{lem: set directions},
    it holds $S_{v,\lambda} \not\ni 0$ and is of dimension $\dim(G_{\lambda}) < d-1$ by assumption.
    To this end, 
    Prop.~\ref{prop: measure zero affine space}~i) yields that 
    \begin{equation*}
        \varphi(S_{v,\lambda})
        = \bigl\{\tfrac{x}{\norm{x}} \;\scalebox{1.2}{$\mid$}\; x \in S_{v,\lambda}\bigr\} 
        \subset \bb S^{d-1}
    \end{equation*}
    is a measure zero set with respect to $\mc U(\bb S^{d-1})$ 
    the uniform distribution on $\bb S^{d-1}$.
    Hence
    \begin{equation*}
        \bb P_{v^{k+1} \sim V^{k+1} \mid V^k = v^k}(v^{k+1} \in G_\lambda)
        = \bb P_{x^k \sim \mc U(\bb S^{d-1})}(x^k \in \varphi(S_{v,\lambda}))
        = 0,
        \qquad v \not \in G_\lambda,
    \end{equation*}
    and by the law of total probability 
    we obtain 
    \begin{equation*}
        \bb P_{v^{k+1}\sim V^{k+1}}(v^{k+1} \in G_\lambda)
        = \int_{\bb S^{d-1} \setminus G_{\lambda}} 
        \bb P_{v^{k+1} \sim V^{k+1} \mid V^k = v^k}(v^{k+1} \in G_\lambda)
        \; \mathrm{d} \bb P_{v^k \sim V^k}(v^k)
        = 0.
    \end{equation*}
    Finally,
    by the $\sigma$-subadditivity of the probability measure 
    it holds $\bb P_{v^{k+1} \sim V^{k+1}}(v^{k+1} \in G) = 0$,
    yielding the assertion.

    Assume, 
    secondly, $\# \spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2}) = 1$: 
    This is the pathological case, 
    and any $v \in \bb S^{d-1}$ is a generalized eigenvector, 
    and so a.s. is $v^0$ by construction.
\end{proof}


As a first and immediate consequence
we can provide the following convergence result for the generated sequence 
of functional values 
\begin{equation}
    \label{eq: update}
    \bigl(f(v^k)\bigr)_{k \in \bb N} 
    = \Bigl(\tfrac{\norm{A v}^2}{\norm{B v}^2}\Bigr)_{k \in \bb N}
    = \Bigl(\tfrac{\scp{v}{A^{\tT}A v}}{\scp{v}{B^{\tT}B v}}\Bigr)_{k \in \bb N}
    = \bigl(\tfrac{a_k}{d_k}\bigr)_{k \in \bb N}.
\end{equation}
Due to Prop.~\ref{prop: update}
it suffices to discuss the cases
where we not have the convergence to the leading generalized eigenspace $G_{\lambda_1}$
after finitely many iterations,
i.e. where $\dim(G_\lambda) < d-1$, or sufficiently $\dim(G_{\lambda_1}) < d-1$.

\begin{corollary}
    \label{cor: monoton conv}
    Let $\dim(G_{\lambda_1}) < d-1$ 
    and $(a_k)_{k \in \bb N}$ and $(b_k)_{k \in \bb N}$ are the sequence of random variables 
    generated by Alg.~\ref{alg: main}. 
    Then the sequence $(\tfrac{a_k}{d_k})_{k \in \bb N}$
    from \eqref{eq: update} converges strictly monotonically increasing, a.s.
\end{corollary}



\subsection{Almost Sure Optimal Convergence}
\label{sec: as optimal convergence}

Differently to the theoretical results from \cite[Lem.~2.12~\&~2.13]{B9} and \cite[Thm.~5.1~\&~5.2]{B9},
it is not possible to prove from the next convergence result,
that $\alpha_k = b_kd_k - a_ke_k \to 0$ for $k \to \infty$,
almost surely.
However, the lemma afterwards claims the vanishing property of $\alpha_k$
as $k \to \infty$ a.s.
using a different proof technique.


\begin{proposition}
    \label{prop: all conv tau}
    Let $\dim(G_{\lambda_1}) < d-1$ 
    and $(a_k)_{k \in \bb N},(b_k)_{k \in \bb N},(c_k)_{k \in \bb N},$ and $(b_k)_{k \in \bb N}$ are the sequence of random variables
    and $(\tau_k)_{k \in \bb N}$ defined as in Thm.~\ref{thm: svd}. 
    It holds 
    $$
        0 < \tau_k [b_k(d_k + \tau_k^2 f_k) - e_k(a_k + \tau_k^2 c_k)] \to 0,
        \qquad \text{as} \qquad 
        k \to 0, 
        \quad \text{a.s.}
    $$
\end{proposition}
\begin{proof}
    It holds by construction and Cor.~\ref{cor: monoton conv} that
    \begin{align}
        \label{eq: frac}
        0 &< \frac{\norm{A(v^k + \tau_k x^k)}^2}{\norm{B(v^k + \tau_k x^k)}^2} - \frac{\norm{A v^k}^2}{\norm{B v^k}^2}
        = f(v^{k+1}) - f(v^k) 
        = \frac{a_k + 2 \tau_k b_k + \tau_k^2 c_k}{d_k + 2 \tau_k e_k + \tau_k^2 f_k} - \frac{a_k}{d_k} \notag \\
        &\qquad= \frac{2\tau_k(b_k d_k - a_k e_k) + \tau_k^2 (c_k d_k - a_k f_k)}{d_k(d_k + 2 \tau_k e_k + \tau_k^2 f_k)} %\notag \\
        = \tau_k \frac{b_k(d_k + \tau_k^2 f_k) - e_k(a_k + \tau_k^2 c_k)}{d_k(d_k + 2 \tau_k e_k + \tau_k^2 f_k)}.
    \end{align}
    Furthermore, by~\eqref{eq: sum d e f},
    the denominator is bounded away from zero a.s.,
    due to Rem.~\ref{rem: norm not zero},
    such that by \eqref{eq: frac}
    $\tau_k [b_k(d_k + \tau_k^2 f_k) - e_k(a_k + \tau_k^2 c_k)] > 0$.
    As the latter is also bounded from above 
    since all parameters are bounded from above,
    the assertion follows from \eqref{eq: frac} and Cor.~\ref{cor: monoton conv}.
\end{proof}


\begin{theorem}
    \label{thm: a_k conv}
    Let $\dim(G_{\lambda_1}) < d-1$
    and $(a_k)_{k \in \bb N},(b_k)_{k \in \bb N},(c_k)_{k \in \bb N},$ 
    and $(b_k)_{k \in \bb N}$ are the sequence of random variables.
    Then $\alpha_k = b_kd_k - a_ke_k \to 0$ for $k \to \infty$, a.s.
\end{theorem}

For proving the almost sure convergence of $\alpha_k = s_k'(0) d_k \to 0$ for $k \to \infty$ (a.s.),
the technical lemmas, cf.~Lem.~\ref{lem: lipschitz func} and~\ref{lem: lipschitz grad},
for the first-order Taylor expansion of $s_k(\tau)$ are used
providing the following corollary on the boundedness property.

\begin{corollary}
    \label{cor: R_k}
    Independent from $k \in \bb N$,
    there exists an $L > 0$ such that 
    \begin{equation*}
        s_k(\tau) - s_k(0) \geq s_k'(0) \tau - \tfrac{L}{2} \tau^2,
        \qquad \forall \tau \in \bb R.
    \end{equation*}
\end{corollary}
\begin{proof}
    Instead of some iteration $k$ with instance $v^k \in \bb S^{d-1}$,
    consider $\tau \mapsto f(v + \tau x) = f(\tfrac{v + \tau x}{\norm{v + \tau x}})$.
    This is a concatenation of the objective $f$, cf.~\ref{eq: obj},
    and $\tau \mapsto v + \tau x$ for $v, x \in \bb S^{d-1}$.
    Then,
    by Taylors expansion,
    we obtain 
    \begin{equation*}
        s_k(\tau) - s_k(0) 
        = \tau s_k'(0) + \tfrac{\tau^2}{2} s_k''(\vartheta \tau),
        \qquad \text{for some} \qquad 
        \vartheta \in (0,1).
    \end{equation*}
    By the chain rule 
    and Lem.~\ref{lem: lipschitz grad},
    we have 
    \begin{equation*}
        |s_k''(\vartheta \tau)|
        \leq |x^{\tT} \nabla^2 f(v + \vartheta \tau x) x|
        \leq L \norm{x}^2
        = L,
    \end{equation*}
    where $L > 0$ is the Lipschitz constant from Lem.~\ref{lem: lipschitz grad}.
    Hence,
    we obtain $s_k''(\vartheta\tau) > - L$.
\end{proof}

    
\begin{proof}[Proof of Thm.~\ref{thm: a_k conv}]
    Assume that $\abs{s_k'(0)}$ does not converge to zero,
    then there is a subsequence $(s^\prime_{k_j})_{j \in \bb N}$ 
    such that $\abs{s_{k_j}^\prime(0)} \geq \varepsilon$ for all $j \in \bb N$
    and some $\varepsilon > 0$. 
    Next, 
    choose some $\tau \in \bb R$ with $0 < \tau < \frac{\varepsilon}{L}$,
    where $L > 0$ is the Lischitz constant from Lem.~\ref{lem: lipschitz grad}.
    Furthermore, 
    define $ (\tilde \tau_k)_{k \in \bb N} \coloneqq (\sign(s_{k}^\prime(0)) \cdot \tau)_{k \in \bb N}$. 
    Then, 
    by applying Lem.~\ref{cor: R_k},
    it follows
    \begin{align*}
        s_k(\tilde \tau_k) - s_k(0) 
        \geq  s_k^\prime(0) \cdot \tilde \tau_k - \frac{L}{2} \tilde \tau_k^2
        \geq |s'_k(0)| \cdot |\tau| - \frac{\varepsilon}{2}|\tau| 
    \end{align*}
    for any $k \in \bb N$,
    and since $\tau_{k}$ is the maximizer for any $k \in \bb N$
    and therewith for any $k_j$,
    conclude that
    \begin{align*}
        s_{k_j}(\tau_{k_j}) - s_{k_j}(0) 
        \geq s_{k_j}(\tilde \tau_{k_j}) - s_{k_j}(0) 
        \geq |s'_{k_j}(0)| \cdot |\tau| - \frac{\varepsilon}{2}|\tau| 
        \geq \varepsilon \abs{\tau} - \frac{\varepsilon}{2}|\tau| 
        \geq \tfrac{\varepsilon}{2}\abs{\tau}
        > 0.
        \end{align*}
    for any $j \in \bb N$.
    Taking the limit on both side,
    yields a contradiction by Cor.~\ref{cor: monoton conv}.
    This implies that $\lim_{k \to \infty} s_k'(0) = 0$.
    By the boundedness of $\norm{B}^2 \geq d_k \geq \lambda_d(B^{\tT}B) > 0$
    immediately follows the assertion.
\end{proof}

\begin{lemma}
    \label{lem: EE_a_k}
    Let $\dim(G_{\lambda_1}) < d-1$
    and $(v^k)_{k \in \bb N}$
    and $(x^k)_{k \in \bb N}$ be the sequence of random variables 
    generated by Alg.~\ref{alg: main}.
    It holds 
    \begin{align*}
        \bb E_{x^k \sim \mc U(\bb S^{d-1}) \mid V^k = v^k}\Bigl[\abs{\tfrac{\alpha_k}{d_k}}^2\Bigr] 
        &= \tfrac{1}{d}\norm[\Big]{\Bigl(\tfrac{\scp{v^k}{A^{\tT}Av^k}}{\scp{v^k}{B^{\tT}Bv^k}} B^{\tT}B - A^{\tT}A\Bigr)v^k}^2 \\
        &= \tfrac{d_k^4}{4d} \norm{\grad f(v^k)}^2
        \to 0,
        \qquad k \to \infty.
    \end{align*}
\end{lemma}
\begin{proof}
    For the $L^1$-convergence,
    recall that Thm.~\ref{thm: a_k conv} shows
    $\alpha_k = b_k d_k - a_k e_k \to 0$ for $k \to \infty$ (a.s.).
    Since 
    \begin{align*}
        \abs[\Big]{\Bigl\langle x^k, \Bigl(\tfrac{\scp{v^k}{A^{\tT}Av^k}}{\scp{v^k}{B^{\tT}Bv^k}} B^{\tT}B - A^{\tT}A\Bigr)v^k \Bigr\rangle}
        &= \frac{\abs{b_k d_k - a_k e_k}}{d_k} %\\
        = \frac{\abs{\alpha_k}}{\scp{x^k}{B^{\tT}B x^k}} \\
        &\leq \frac{\abs{\alpha_k}}{\lambda_d(B^{\tT}B)} 
        \leq 2\kappa(B^{\tT}B) \norm{A^{\tT}A},
    \end{align*}
    Lebesgue's dominated convergence theorem
    together with the law of total expectation yields the first assertion.
    %
    For the second equality,
    rewrite the conditional expectation 
    w.r.t. the conditional law, which is independently from $v^k$ given by the uniform distribution on the unit sphere
    \begin{align*}
        &\bb E_{x^k \sim \mc U(\bb S^{d-1}) \mid V^k = v^k}[(\tfrac{\alpha_k}{d_k})^2]\\
        &= \bb E_{x^k \sim \mc U(\bb S^{d-1}) \mid V^k = v^k}
        \scalebox{0.92}{$\Bigl[\Bigl\langle \Bigl(\tfrac{\scp{v^k}{A^{\tT}Av^k}}{\scp{v^k}{B^{\tT}Bv^k}} B^{\tT}B - A^{\tT}A\Bigr)v^k, x^k \Bigr\rangle
        \Bigl\langle x^k, \Bigl(\tfrac{\scp{v^k}{A^{\tT}Av^k}}{\scp{v^k}{B^{\tT}Bv^k}} B^{\tT}B - A^{\tT}A\Bigr)v^k \Bigr\rangle\Bigr]$}
        \\
        &= (v^k)^{\tT}\Bigl(\tfrac{\scp{v^k}{A^{\tT}Av^k}}{\scp{v^k}{B^{\tT}Bv^k}} B^{\tT}B - A^{\tT}A\Bigr)
        \bb E_{x^k \sim \mc U(\bb S^{d-1})}[x^k(x^k)^{\tT}] 
        \Bigl(\tfrac{\scp{v^k}{A^{\tT}Av^k}}{\scp{v^k}{B^{\tT}Bv^k}} B^{\tT}B - A^{\tT}A\Bigr)v^k 
        \\
        &= \tfrac{1}{d} \norm[\Big]{\Bigl(\tfrac{\scp{v^k}{A^{\tT}Av^k}}{\scp{v^k}{B^{\tT}Bv^k}} B^{\tT}B - A^{\tT}A\Bigr)v^k}^2 \\
        &= \tfrac{1}{d} \norm[\big]{(A^{\tT}A - f(v^k) B^{\tT}B) v^k}^2
        = \tfrac{1}{d} \norm[\big]{H(v^k) v^k}^2,
    \end{align*}
    using \eqref{eq: x^k}~f. 
    Finally,
    we utilize \eqref{eq: riemannian gradient}~f., 
    i.e. $\tfrac{d_k^2}{2} \grad f(v^k) = H(v^k) v^k$ from \eqref{eq: riemannian hess}~f.
\end{proof}

\begin{figure}[h]
    \centering
    \includegraphics[width=\linewidth]{plots/sphere_leading_eigenspace_iter.pdf}
    \caption{Visualization of the great circle $\bb S^1$ of the $\bb S^3$ 
    with the iterates $v^k \in \bb S^3 \hookrightarrow \bb S^1$,
    whenever $\abs{v_3^k}+\abs{v_4^k} < 10^{-3}$, generated by Alg.~\ref{alg: main}
    for $A = \diag(1,1,0,0)$ and $B = I_4$.
    Here visualizations are provided for the iterations $k \in \{1.000, 1.500,2.000,...,10.000\}$
    (starting: top left, towards: bottom right).}
    \label{fig: leading eigenspace iter}
\end{figure}


The existence of a subsequence, proven in the following proposition,
can be observed in Fig.~\ref{fig: leading eigenspace iter}.
As Alg.~\ref{alg: main} convergences after finitely many iterations 
or $\gamma_k \neq 0$ for all $k \in \bb N$ (a.s.), see Prop.~\ref{prop: update} and Cor.~\ref{cor: monoton conv},
the following convergence result can be claimed.
Here, the distance of the iterates $v^k$ to the leading set of generalized eigenspaces
is measured by
\vspace{-3pt}
\begin{equation*}
    \dist(\mc C, y) \coloneqq \inf_{x \in \mc C} \norm{y - x},
    \vspace{-2pt}
\end{equation*}
which is finite for closed convex sets in finite dimensions and attended by some $s \in \mc C$.
Differently \cite{B8,B9},
we are not aware of the convergence for the sequence of random vectors,
even if the dimension of the leading generalized eigen space is one.
This is due to the unconstrained sampling technique, cf.~Fig.~\ref{fig: leading eigenspace iter}


\begin{proposition}
    \label{prop: as conv eigenspace}
    Let $\dim(G_{\lambda_1}) < d-1$
    and $(v^k)_{k \in \bb N}$ be the sequence of random variables 
    generated by Alg.~\ref{alg: main}.
    Then there exists a subsequence $(v^{k_j})_{j \in \bb N}$
    and a random variable $\lambda$ a.s. taking values in $\spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2})$
    such that 
    $\dist(G_\lambda, v^{k_j}) \to 0$ for $j \to \infty$ a.s.
    Moreover,
    the sequence $(\tfrac{a_k}{d_k})_{k \in \bb N}$ from \eqref{eq: update}
    converges to $\lambda$ a.s.
\end{proposition}
\begin{proof}
    The proof technique is simliar to \cite[Prop.~5.4]{B9};
    see §~\ref{sec: app}.
\end{proof}

\begin{theorem}
    \label{thm: convergence as}
    Let $(v^k)_{k \in \bb N}$ be the sequence of random variables generated by Alg.~\ref{alg: main}.
    Then 
    \begin{equation*}
        \tfrac{\norm{A v^k}^2}{\norm{B v^k}^2} 
        \nearrow \lambda_1,
        \quad \text{and} \quad
        \dist(G_{\lambda_1}, v^k) \to 0,
        \quad \text{as} \quad 
        k \to \infty,
        \quad (a.s.).
    \end{equation*}
\end{theorem}


For proving the main convergence result Thm.~\ref{thm: convergence as}, 
the following constructive lemma is required,
which is visualized in Fig.~\ref{fig: sphere_proj}.
It is similar to \cite[Lem.~5.5]{B9} 
and the statement from \cite[Lem.~2.17]{B8}
using the geodesic distances.
It shows, that the probability to sample into an $\varepsilon$-neighborhood 
of an optimal generalized eigenvector is uniformly lower bounded away from zero
w.r.t. the uniform distribution on the unit sphere.


\begin{figure}[htb]
    \centering
    \includegraphics[width=0.65\linewidth,clip=true, trim=5pt 5pt 5pt 30pt]{plots/sphere_ball.pdf}
    \caption{Visualization of the claim in Lem.~\ref{lem: uniform lower bound} for an uniform lower bound
    of probability that reaching $\bb B_\varepsilon(\tilde v)$ for any $v \in \bb S^{d-1}$ is provided.
    This is the situation in the proof of Thm.~\ref{thm: convergence as} 
    as it is used in \eqref{eq: uniform lower bound}.}
    \label{fig: sphere_proj}
\end{figure}

\begin{lemma}
    \label{lem: uniform lower bound}
    Let $v, \tilde v \in \bb S^{d-1}$ and $\varepsilon > 0$. 
    Define 
    \begin{align*}
        \mc D_v \coloneqq \left\{ x \in \bb S^{d-1} 
        \;\middle|\; 
        \exists \tau \in \bb R, 
        R_v(\tau x) 
        = \tfrac{v + \tau x}{\norm{v + \tau x}} \in \bb B_\varepsilon(\tilde v) \cup \bb B_\varepsilon(-\tilde v)\right\}.
    \end{align*}
    There exists some $p_{\varepsilon,d} > 0$ 
    such that $\inf_{v \in \bb S^{d-1}} \sigma_{d-1}(\mc D_v) > p_{\varepsilon,d}$.
\end{lemma}
\begin{proof}
    See §~\ref{sec: app}.
\end{proof}



Finally, for proving Thm.~\ref{thm: convergence as},
we consider the set 
\begin{align*}
    \label{eq: set L}
    \mc L 
    \coloneqq 
    \left\{v \in \bb S^{d-1} 
    \;\middle|\; 
    \tfrac{\norm{A v^k}^2}{\norm{B v^k}^2} 
    = \tfrac{\scp{v}{A^{\tT}Av}}{\scp{v}{B^{\tT}Bv}} 
    = f(v) 
    > \lambda_2\right\}.
\end{align*}
and utilize Lem.~\ref{lem: uniform lower bound}
and refer to \cite[Thm.~2.17]{B8}
in light of a similar proof technique. 
On the other hand, one might prove it quite similar by utilizing 
the Borel--Cantelli lemma \cite[VII.~§~5]{renyi1966wahrscheinlichkeitsrechnung}.

\begin{proof}[Proof of Thm.~\ref{thm: convergence as}]
    Take the set $\mc L$ (above) into account 
    and define the events $E_k \coloneqq \{V^k \not\in \mc L\}$.
    Then,
    by the monotonicity of the generated functional values, cf.~Cor.~\ref{cor: monoton conv},
    we have $E_{k+1} \subseteq E_k$.
    Furthermore,
    we have 
    \begin{equation}
        \label{eq: E_k+1}
        \bb P(E_{k+1})
        = \bb P_{V^{k+1}}(v^{k+1} \not\in \mc L)
        = \int_{\bb S^{d-1} \setminus \mc L}
        \bb P_{V^{k+1} \mid V^k = v^k} (v^{k+1} \not\in \mc L)
        \; \mathrm d \bb P_{V^k}(v^k),
    \end{equation}
    since we have 
    \begin{equation*}
        \bb P_{V^{k+1} \mid V^k = v^k} (v^{k+1} \not\in \mc L)
        = 0,
        \qquad \text{if} \qquad 
        v^k \in \mc L.
    \end{equation*}
    Furthermore,
    we have by the continuity of $f$, cf.~\ref{eq: obj}, from Lem.~\ref{lem: lipschitz func}
    some $\varepsilon > 0$ and $\tilde v \in \bb S^{d-1}$ such that 
    \begin{equation*}
        \bb B_{\varepsilon,\pm \tilde v} 
        \coloneqq (\bb B_{\varepsilon}(\tilde v) \cup \bb B_{\varepsilon}(-\tilde v)) 
        \cap \bb S^{d-1} 
        \subset \mc L
    \end{equation*}
    and hence 
    \begin{align*}
        \bb P_{v^{k+1} \sim V^{k+1} \mid V^k = v^k} (v^{k+1} \not \in \mc L)
        &= \bb P_{x^{k} \sim \mc U(\bb S^{d-1}) \mid V^k = v^k} (R_{v^k}(\tau_k x^k) \not \in \mc L) \\
        &\leq \bb P_{x^k \sim \mc U(\bb S^{d-1})} (x^k \not \in \mc D_{v^k}) \\
        &\leq \bb P_{x^k \sim \mc U(\bb S^{d-1})} (x^k \not \in \bb B_{\varepsilon,\pm \tilde v})
        < 1 - p_{\varepsilon,d}
    \end{align*}
    by utilizing Lem.~\ref{lem: uniform lower bound}
    for some $p_{\varepsilon,d} \in (0,1)$.
    Therewith,
    by \eqref{eq: E_k+1} we obtain 
    \begin{equation*}
        \bb P(E_{k+1})
        < (1 - p_{\varepsilon, d}) \bb P_{V^k}(v^k \not \in \mc L)
        = (1 - p_{\varepsilon, d}) \bb P(E_{k}),
        \qquad k \in \bb N.
    \end{equation*}
    Hence, we iteratively have 
    $\bb P(E_k) < (1 - p_{\varepsilon, d})^k \bb P(E_0)$, 
    where $\bb P(E_0) \leq 1$.
    Now, Borel--Cantelli lemma \cite[VII.~§~5]{renyi1966wahrscheinlichkeitsrechnung}
    yields the assertion,
    due to 
    \begin{equation*}
        \sum_{k = 0}^\infty \bb P (E_k)
        < \bb P(E_0)\sum_{k = 1}^\infty (1 - p_{\varepsilon,d})^k
        = \bb P(E_0) \frac{1}{1 - (1 - p_{\varepsilon,d})}
        = \frac{\bb P(E_0)}{p_{\varepsilon, d}}
        < \infty,
    \end{equation*}
    such that 
    $f(v^k) = \nicefrac{\scp{v^k}{A^{\tT}A v^k}}{\scp{v^k}{B^{\tT}B v^k}} \nearrow \lambda_1$ as $k \to \infty$ a.s.,
    by Prop.~\ref{prop: as conv eigenspace}.

    For the second assertion,
    we observe that for an orthonormal basis $\{u_1,...,u_d\} \subset \bb S^{d-1}$
    of eigen vectors of $(B^{\tT}B)^{-1/2} A^{\tT}A (B^{\tT}B)^{-1/2}$,
    we define due to \eqref{eq: eigen}~ff. $w^k \coloneqq (B^{\tT}B)^{1/2} v^k$ such that 
    \begin{align*}
        f(v^k)
        &= \frac{\scp{v^k}{A^{\tT}A v^k}}{\scp{v^k}{B^{\tT}B v^k}}
        = \frac{\scp{w^k}{(B^{\tT}B)^{-1/2}A^{\tT}A (B^{\tT}B)^{-1/2} w^k}}{\norm{w^k}^2} \\
        &= \frac{\sum_{i,j = 1}^d \scp{w^k}{u_i} \scp{w^k}{u_j} \lambda_j \scp{u_i}{u_j}}{\norm{w^k}^2}
        = \frac{\sum_{i = 1}^d \scp{w^k}{u_i}^2 \lambda_i}{\norm{w^k}^2}
        \leq \lambda_1. 
    \end{align*}
    As we know the convergence a.s. for $f(v^k) \nearrow \lambda_1$ as $k \to \infty$,
    we conclude that $|\langle w^k, u_i\rangle| \to 0$ as $k \to \infty$
    if $u_i$ is not an eigenvector corresponding to $\lambda_1$.
\end{proof}


\subsection{Estimating the Riemannian Gradient and Hessian}

Similar to \cite{B9},
Alg.~\ref{alg: main} can be varied using $m$ iid. sampled search directions 
to estimate a Riemannian gradient, which speeds Alg.~\ref{alg: main} up, 
especially due to the closed formulae for the optimal step size.
This idea is based on \cite{B9} utilizing Thm.~\ref{thm: riemannian style}.
The approach is summarized in Alg.~\ref{alg:cmgRq}.
Therefore, Alg.~\ref{alg:cmgRq} can be seen as a zeroth-order method 
using an approximation of the Riemannian gradient.
As Thm.~\ref{thm: svd} provides the optimal step size 
for the approximation of the sampled step direction,
the proposed method is the optimal possible constrution 
for a zeroth-order method using an unbiased estimator 
for the Riemannian gradient.
Recall that due to the new sampling procedure, the distribution is not uniformly; 
however, it remains absolutely continuous
such that the bad events ($\gamma_k = 0$, i.e. $v^k$ is a generalized eigenvector) 
remain as measure zero sets.
Hence the almost sure convergence of Alg.~\ref{alg:cmgRq} can be obtained
from the theory, which is here provided for a single sample direction.

\begin{algorithm}[htb]
    \caption{Unconstrained zeroth-order, $m$-approximative calculation of the generalized operator norm}\label{alg:cmgRq}
    \begin{algorithmic}[1]
    \State{\textbf{Given} $A \in \bb R^{m \times d}$ and $B \in \bb R^{\ell \times d}$ such that $\rank(B) = d$.}
    \State{\textbf{Initialize} $v^{0}\in\bb R^{d}$ with $\norm{v^0}=1$.}
    \For{$k=0,1,2,\dots$}
    \State\textbf{Sample} $y_i\sim \mc N(0,I_d)$ for $i=1,...,m$ iid.
    \State\textbf{Project} $x^k_i = y_i / \norm{y_i}$,
    calculate all $\alpha_{k,i}$ and the zeroth-order $m$-approximation of the Riemannian gradient by 
    $
        x^k_m \coloneqq \tfrac{1}{m}\sum_{i = 1}^m \alpha_{k,i} x^k_i
    $
    and \textbf{project} $x^k \coloneqq  x^k_m/\norm{x^k_m}$.
    \State\textbf{Calculate} step size $\tau_{k}$ from Thm.~\ref{thm: svd} using the parameters from \eqref{eq: para mgRq}.
    \State\textbf{Update} iterate $v^k$ with $\tau_k x^k$ via \eqref{eq: retraction}.
    \EndFor
    \State\textbf{Return} estimate of $\norm{A/B} \approx \tfrac{\norm{A v^k}}{\norm{B v^k}} = \sqrt{\tfrac{a_k}{d_k}}$
    \end{algorithmic}
\end{algorithm}

\begin{theorem}
    \label{thm: riemannian style}
    It holds 
    $\bb E_{x^k \sim \mc U(\bb S^{d-1}) \mid V^k = v^k}\bigl[\tfrac{\alpha_k}{d_k} x^k\bigr] 
    = \tfrac{d_k^2}{2d} \nabla f(v^k) 
    = \tfrac{d_k^2}{2d} \textup{grad} f(v^k)$.
\end{theorem}
\begin{proof}
    For the first statement,
    simply rewrite the conditional expectation
    \begin{align*}
        &\hspace{-20pt}\bb E_{x^k \sim \mc U(\bb S^{d-1}) \mid V^k = v^k}[\alpha_k x^k]
        = \bb E_{x^k \sim \mc U(\bb S^{d-1})\mid V^k = v^k}[(b_k d_k - a_k e_k) x^k] \\
        &= \bb E_{x^k \sim \mc U(\bb S^{d-1})\mid V^k = v^k}[x^k (x^k)^{\tT} \bigl(\langle B^{\tT}B v^k, v^k\rangle A^{\tT}A v^k - \langle A^{\tT}A v^k, v^k\rangle B^{\tT}B v^k\bigr)] \\
        &= \bb E_{x^k \sim \mc U(\bb S^{d-1})}[ x^k (x^k)^{\tT}] \bigl(\langle B^{\tT}B v^k, v^k\rangle A^{\tT}A v^k - \langle A^{\tT}A v^k, v^k\rangle B^{\tT}B v^k\bigr) \\
        &= \tfrac{1}{d} \bigl(\langle B^{\tT}B v^k, v^k\rangle A^{\tT}A v^k - \langle A^{\tT}A v^k, v^k\rangle B^{\tT}B v^k\bigr) \\
        &= \tfrac{d_k}{d} \bigl(A^{\tT}A v^k - \tfrac{a_k}{d_k} B^{\tT}B v^k\bigr)
        = \tfrac{d_k}{d} H(v^k) v^k,
    \end{align*}
    using \eqref{eq: x^k}~f.
    and \eqref{eq: para mgRq}~f., 
    as well as \eqref{eq: riemannian gradient} and \eqref{eq: update},
    i.e. $\frac{d_k^2}{2} \grad f(v^k) = H(v^k) v^k$.
\end{proof}

We further 
derive an unbiased estimator of the Riemannian Hessian \eqref{eq: riemannian hess special} for \eqref{eq: prob sphere}.
The idea is to obtain a Newton-style 
or quasi-Newton zeroth-order method \cite{gill1972quasinewton,Antoniou2007},
where we capture more information 
for the sampled direction 
by solving a system of linear equations.
The following result studies the expectation 
of second- and fourth-order samples
for an arbitrary, quadratic matrix.

\begin{proposition}
    \label{prop: rie hess}
    Let $A \in \bb R^{d \times d}$
    and $\symA \coloneqq \tfrac{1}{2}(A + A^{\tT})$ denotes the hermitian part of $A$.
    It holds
    \begin{equation*}
        \bb E_{x \sim \mc U(\bb S^{d-1})}[\scp{x}{Ax}] = \frac{\trace(\symA)}{d} = \frac{\trace(A)}{d}
        \quad\text{and}\quad
        \bb E_{x \sim \mc U(\bb S^{d-1})}[\scp{x}{Ax} xx^{\tT}] = \frac{2\symA + \trace(A)I_d}{d(d+2)}.
    \end{equation*}
\end{proposition}
\begin{proof}
    See §~\ref{sec: app}.
\end{proof}


As a direct consequence 
we obtain the unbiased estimator 
for the inducing matrix $H(v)$
of the Riemannian Hessian from \eqref{eq: riemannian hess special},
using the sampling from \eqref{eq: x^k}
as well as for the Riemannian Hessian itself,
using the sampling from \eqref{eq: tangent surrogate} inside the tangent space.

\begin{corollary}
    \label{cor: riemannian hessian estimator}
    Let $A \in \bb R^{m \times d}$ and $B \in \bb R^{\ell \times d}$
    It holds 
    \begin{align*}
        \bb E_{x \sim \mc U(\bb S^{d-1})}
        \Bigl[\bigl(\norm{A x}^2 - f(v)\norm{B x}^2\bigr)(xx^{\tT} - \tfrac{1}{d+2} I_d)\Bigr]
        = \frac{2}{d(d+2)} H(v).
    \end{align*}
    and 
    \begin{align*}
        \bb E_{y \sim \mc U(\bb T_v \cap \bb S^{d-1})}
        \Bigl[\bigl(\norm{A y}^2 - f(v)\norm{B y}^2\bigr)(yy^{\tT} - \tfrac{1}{d+1} P_v)\Bigr]
        &= \frac{\norm{B v}^2}{(d-1)(d+1)} \hess f(v).
    \end{align*}
\end{corollary}
\begin{proof}
    See §~\ref{sec: app}.
\end{proof}


\begin{algorithm}[htb]
    \caption{Zeroth-Second-order, $m$-approximate calculation of the generalized operator norm}\label{alg:czmgRq}
    \begin{algorithmic}[1]
    \State\textbf{Initialize} $v^{0}\in\bb R^{d}$ with $\norm{v^0}=1$
    \For{$k=0,1,2,\dots$}
    \State\textbf{Sample} $y_i^1, y_i^2 \overset{\text{iid.}}{\sim} \mc N(0,I_d)$ for $i=1,...,m$ iid.
    \State\textbf{Project} each $x^{k,1}_i = y_i^1 / \norm{y_i^1}$, 
    and calculate all $\alpha_{k,i}$ and the zeroth-order $m$-approximation of the Riemannian gradient by 
    $
        x^k_m \coloneqq \tfrac{1}{m}\sum_{i = 1}^m \alpha_{k,i} x^{k,1}_i.
    $
    \State\textbf{Project} each $x^{k,2}_i = P_{v^k} y_i^2 / \norm{ P_{v^k} y_i^2}$,
    and calculate all $c_{k,i}, f_{k,i}$
    and the zeroth-order $m$-approximation of the Riemannian Hessian by 
    $$
        H_m^k 
        \coloneqq 
        \tfrac{1}{m} 
        \sum_{i = 1}^m (c_{k,i} - \tfrac{a_k}{d_k}f_{k,i}) (x^{k,2}_i(x^{k,2}_i)^{\tT} - \tfrac{1}{d-1} P_{v^k}).
    $$
    \State\textbf{Solve} $H_m^k x = x_m^k$ for $x \in \bb R^d$ and set $x^k \coloneqq x/\norm{x}$.
    \State\textbf{Calculate} step size $\tau_{k}$ from Thm.~\ref{thm: svd} using the parameters from \eqref{eq: para mgRq}.
    \State\textbf{Update} iterate $v^k$ with $\tau_k x^k$ via \eqref{eq: retraction}.
    \EndFor
    \State\textbf{Return} estimate of $\norm{A/B} \approx \tfrac{\norm{A v^k}}{\norm{B v^k}} = \sqrt{\tfrac{a_k}{d_k}}$.
    \end{algorithmic}
\end{algorithm}

As for the variance-reduced random step directions in Alg.~\ref{alg:czmgRq}
using Thm.~\ref{thm: riemannian style},
the random step directions 
fulfilling the linear equation 
involving the variance-reduced estimator for the Riemannian gradient and Hessian 
is not uniformly drawn anymore.
However, it remains absolutely continuous 
and, hence, the update procedure 
with the optimal step size is still well-defined, almost surely.


\section{Numerical Experiments}
\label{sec: num}

The success of the proposed generalizations of \cite{B8,B9}
is shown on synthetic datasets,
i.e. random Gaußian matrices $A \in \bb R^{d\times d}$
and $B \in \bb R^{2d \times d}$,
where $50$ runs of the different algorithms are performed.
The resulting \emph{relative quotient error},
defined as 
\begin{equation*}
    \textrm{RQE}_k 
    \coloneqq 
    \frac{\norm{A/B}^2 - \tfrac{\norm{A v^k}^2}{\norm{B v^k}^2}}{\norm{A/B}^2},
    \quad \text{and} \quad
    \textrm{MSQR}_k 
    \coloneqq 
    \min_{n\leq k} \; \norm[\Big]{A^{\tT}A v^n - \tfrac{\norm{A v^n}^2}{\norm{B v^n}^2} B^{\tT}B v^n}^2,
\end{equation*}
the relative error of the generalized eigen equation,
i.e. the \emph{minimal squared residual} in the eigenvector equation,
as well as the sequence $(\alpha_k) = (b_kd_k - a_ke_k)_{k \in \bb N}$, respectively $\abs{b_k}$ from \cite{B9}, are compared.
Furthermore, 
the sequence of step sizes is reported in Fig.~\ref{fig: proof of concept} and~\ref{fig:exp_x}.

All algorithms are implemented in Python and the code is publicly available
\footnote{%
\url{https://github.com/JJEWBresch/ZerothOrderGeneralizedOperatorNorm}.}.
The experiments are performed on an off-the-shelf MacBook Pro 2020 
with Intel Core i5 (4‑Core CPU, 1.4~GHz) and 8~GB~RAM.


\subsection{Proof-of-concept Results}
\label{sec: num proof of concept}

In this first discussion,
we aim to substantiate the success of the proposed methods,
cf.~Alg.~\ref{alg: main},
and the $m$-sampling variance-reduced approach, cf.~Alg.~\ref{alg:cmgRq},
by a proof-of-concept experiment.
We chose $d \in \{10,100,1000\}$ for the Gaußian matrices
introduced in §~\ref{sec: num}.
The resulting means over $50$ runs of Alg.~\ref{alg: main} and~\ref{alg:cmgRq}
for the \emph{relative quotient error} (RQE), the \emph{minimal squared residual} (MSQR),
and the parameter $\alpha_k$%
---detecting critical points, 
by concluding from Thm.~\ref{thm: riemannian style} that 
\begin{align*}
    \label{eq: riemannian gradient estimate}
    \bb E_{x^k \sim \mc U(\bb S^{d-1}) \mid V^k = v^k}[(b_k d_k - a_k e_k)^2]
    &= \bb E_{x^k \sim \mc U(\bb S^{d-1}) \mid V^k = v^k}[\alpha_k^2] 
    = \tfrac{\norm{B v^k}^2}{2d} \norm{\grad f(v^k)}^2.
\end{align*}
Furthermore,
the step sizes per iteration 
are reported.
All estimates are visualized in Fig.~\ref{fig: proof of concept}.

We observe that the tremendous improvement by the $m$-sampling approach 
compared to a single, uniform at random step direction on the unit sphere.
Besides the observable linear convergence rate 
for the relative error for estimating the leading generalized eigenvalue,
the minimal squared residual, 
as well as the estimate for the length of the true Riemannian gradient, 
is doing much better than a sublinear behavior,
as it is proven in \cite{B8,B9,B12}.
Notably,
since we do not report a minimal value until the $k$-th iteration of $\alpha_k = b_k d_k - a_k e_k$ 
(third row, Fig.~\ref{fig: proof of concept}),
we observe a linear convergence behavior to critical points, 
and not only a sublinear convergence rate,
without a square. 
Combined with the (linear) convergence to the global maximum,
as it is proven in Thm.~\ref{thm: convergence as},
this has clear advantages to state-of-the-art methods \cite{li2023stochastic,li2014sketching}
from §~\ref{sec: zeroth order}, 
cf.~Alg.~\ref{alg: zeroth order} from §~\ref{sec: alg}.


\begin{figure}[htb]
    \resizebox{\linewidth}{!}{%
    \begin{threeparttable}
    \begin{tabular}{c c c c}
        & ${d = \tfrac{m}{2} = 10}$ & ${d = \tfrac{m}{2} = 100}$ & ${d = \tfrac{m}{2} = 1000}$ \\
        \rotatebox{90}{\hspace{1.2cm} $\tau_k$ \hspace{1.3cm} $\abs{b_kd_k - a_ke_k}$ \hspace{0.9cm} $\textrm{MSQR}_k$ \hspace{2.1cm} $\textrm{RQE}_k$}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 60pt 30pt 80pt]{plots/gaussian_matrices_over_all_adj_single_10.pdf}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 60pt 30pt 80pt]{plots/gaussian_matrices_over_all_adj_single_100.pdf}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 60pt 30pt 80pt]{plots/gaussian_matrices_over_all_adj_single_1000.pdf}\\
        & Iterations $k$ & Iterations $k$ & Iterations $k$
    \end{tabular}
    \begin{tablenotes}
    \item[] \scalebox{1.2}{\hspace{4cm} $m=1$ \linegraydotted \hspace{2cm} $m=10$ \linegraydashed \hspace{2cm} $m=100$ \linegray}
    \end{tablenotes}
    \end{threeparttable}
    }
    \caption{Proof-of-concept experiment 
    on Alg.~\ref{alg:cmgRq} 
    for different sizes of matrices $(A, B)$.
    For all quantities 
    the mean over $50$ runs
    on random Gaußian matrices $(A, B)$ is reported.
    }
    \label{fig: proof of concept}
\end{figure}


\subsection{Comparison with \cite{B9}}
\label{sec: num comp}

As indicated in §~\ref{sec: num proof of concept}
a comparison with the recently proposed zeroth-order methods \cite{B8,B9}
which already improve state-of-the-art methods \cite{li2023stochastic,boumal2023introduction},
cf.~Alg.~\ref{alg: zeroth order},
is necessary.

It can be observed that the performances of both methods,
the proposed one, cf.~Alg.~\ref{alg: main} respectively~\ref{alg:cmgRq}
and the zeroth-order $m$-sampling approach \cite{B9} for the generalized Rayleigh quotient 
solving \eqref{eq: obj}~ff.,
are comparable in lower dimensions, see Fig.~\ref{fig:exp_x}.
In higher dimensions $m \gg 10$ 
the new sampling procedure,
cf.~\eqref{eq: x^k},
seems to outperform the recent methods 
using \eqref{eq: tangent surrogate} from \cite{B9}.
This observation can be linked to the wider sampling space $\bb S^{d-1}$, 
which is not restricted to the tangent space $\bb T_{v^k}$ at any iteration.
Moreover, the projection in each iteration, especially for \cite[Alg.~2]{B9}, 
requires (at least) matrix-matrix multiplications,
where Alg.~\ref{alg:cmgRq} does not.
This reduces the computation time in higher dimensions
as it can be observed in Fig.~\ref{fig:exp_xt}.
Even though it is not possible to prove the convergence rate 
for the error of the corresponding eigen equation 
similar to \cite{B8,B9,B12},
Fig.~\ref{fig:exp_x} indicates a convergence rate $\mathcal O(\tfrac{1}{k})$ 
for MSQR and a linear rate for RQE.


\begin{figure}
    \resizebox{\linewidth}{!}{%
    \begin{threeparttable}
    \begin{tabular}{c c c c}
        & ${d = \tfrac{m}{2} = 10}$ & ${d = \tfrac{m}{2} = 50}$ & ${d = \tfrac{m}{2} = 100}$ \\
        \rotatebox{90}{\hspace{1.3cm} $\tau_k$ \hspace{0.9cm} ${\color{orange}\abs{b_kd_k - a_ke_k}}, {\color{blue}\abs{b_k}}$ \hspace{0.5cm} $\textrm{MSQR}_k$ \hspace{2.2cm} $\textrm{RQE}_k$}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 60pt 30pt 80pt]{plots/gaussian_matrices_over_all_adj_time_10.pdf}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 60pt 30pt 80pt]{plots/gaussian_matrices_over_all_adj_time_50.pdf}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 60pt 30pt 80pt]{plots/gaussian_matrices_over_all_adj_time_100.pdf}\\
        & Iterations $k$ & Iterations $k$ & Iterations $k$
    \end{tabular}
    \begin{tablenotes}
    \item[] \scalebox{1.2}{\hspace{4cm} $m=1$ \linegraydotted \hspace{2cm} $m=10$ \linegraydashed \hspace{2cm} $m=100$ \linegray}
    \end{tablenotes}
    \end{threeparttable}
    }
    \caption{Comparison 
    of Alg.~\ref{alg: main}, i.e. Alg.~\ref{alg:cmgRq}, (orange) and \cite[Alg.~2]{B9} (blue) 
    for different sizes of matrices $(A, B)$ and $\abs{b_k}$ from Rem.~\ref{rem: connection}, i.e. the length of \eqref{eq: connection grad length}.
    For all quantities 
    the mean over $50$ runs
    on random Gaußian matrices $(A, B)$ is reported.
    }
    \label{fig:exp_x}
\end{figure}

\begin{figure}
    \resizebox{\linewidth}{!}{%
    \begin{threeparttable}
    \begin{tabular}{c c c c}
        \rotatebox{90}{\hspace{1.0cm} $\textrm{MSQR}_t$ \hspace{3.4cm} $\textrm{RQE}_t$}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 40pt 30pt 50pt]{plots/gaussian_matrices_over_all_adj_ttime_10.pdf}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 40pt 30pt 50pt]{plots/gaussian_matrices_over_all_adj_ttime_50.pdf}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 40pt 30pt 50pt]{plots/gaussian_matrices_over_all_adj_ttime_100.pdf} \\
        & Time, sec. $t$ & Time, sec. $t$ & Time, sec. $t$
    \end{tabular}
    \begin{tablenotes}
    \item[] \scalebox{1.2}{\hspace{4cm} $m=1$ \linegraydotted \hspace{2cm} $m=10$ \linegraydashed \hspace{2cm} $m=100$ \linegray}
    \end{tablenotes}
    \end{threeparttable}
    }
    \caption{Proof-of-concept experiment 
    from Fig.~\ref{fig:exp_x} by time rescaling.
    }
    \label{fig:exp_xt}
\end{figure}


\subsection{Second-order Improvement}

Lastly,
we compare the novel sampling approach on the unit sphere, see Alg.~\ref{alg:cmgRq},
with the equipped $m$-sampling variance reduced zeroth-order estimator 
of the Riemannian Hessian, see Alg.~\ref{alg:czmgRq}, cf.~Cor.~\ref{cor: riemannian hessian estimator}.
We, again, report the estimates introduced in the beginning of §~\ref{sec: num}
and run the different algorithms $50$ times for different sizes of Gaußian matrices $(A, B)$.
The results are shown in Fig.~\ref{fig: second comparison}.

We observe that the quasi-Newton variant Alg.~\ref{alg:czmgRq} of Alg.~\ref{alg:cmgRq}
shows a stricter convergence behavior 
not only for the RQE 
but also for the MSQR
compared to the original method.
Especially in higher dimensions, this effect becomes even more visible.
This shows the advantage of including information of the function \eqref{eq: obj} from higher order
and closes the vulnerable point of the original proposed methods,
i.e. Alg.~\ref{alg:cmgRq} and \cite[Alg.~2]{B9},
for reduced convergence speed 
when being close to critical points.
This behavior is well-known from classical first-order Riemannian ascent methods,
as drawn in §~\ref{sec: first order}. i.e. Alg.~\ref{alg: first order} in §~\ref{sec: alg}.
Here, only the maximizers and not the saddle points 
are the problematic regions for the original proposed methods.

\begin{figure}
    \resizebox{\linewidth}{!}{%
    \begin{threeparttable}
    \begin{tabular}{c c c c}
        & ${d = \tfrac{m}{2} = 10}$ & ${d = \tfrac{m}{2} = 50}$ & ${d = \tfrac{m}{2} = 100}$ \\
        \rotatebox{90}{\hspace{0.9cm} $\textrm{MSQR}_k$ \hspace{2.4cm} $\textrm{RQE}_k$}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 300pt 30pt 50pt]{plots/gaussian_matrices_over_all_adj_second_10.pdf}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 300pt 30pt 50pt]{plots/gaussian_matrices_over_all_adj_second_50.pdf}
        & \includegraphics[width=0.5\linewidth, clip=true, trim=10pt 300pt 30pt 50pt]{plots/gaussian_matrices_over_all_adj_second_100.pdf} \\
        & Iterations $k$ & Iterations $k$ & Iterations $k$
    \end{tabular}
    \begin{tablenotes}
    \item[] \scalebox{1.2}{\hspace{4cm} $m=1$ \linegraydotted \hspace{2cm} $m=10$ \linegraydashed \hspace{2cm} $m=100$ \linegray}
    \end{tablenotes}
    \end{threeparttable}
    }
    \caption{Comparison 
    of Alg.~\ref{alg:cmgRq} (olive) and Alg.~\ref{alg:czmgRq} (purple) 
    for different sizes of matrices $(A, B)$.
    For all quantities 
    the mean over $50$ runs
    on random Gaußian matrices $(A, B)$ is reported.
    }
    \label{fig: second comparison}
\end{figure}




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\printbibliography


\appendix

\section{Algorithms}\label{sec: alg} %\label{sec: A1}

\begin{algorithm}[H]
    \caption{First-order Riemannian gradient ascent method}
    \label{alg: first order}
    \begin{algorithmic}
        \State{\textbf{Given} $A \in \bb R^{m \times d}$ and $B \in \bb R^{\ell \times d}$ such that $\rank(B) = d$.}
        \State{\textbf{Initialize} with $v^0 \in \bb S^{d-1}$.}
        \For{$k = 1,2,3,...$}
        \State{\textbf{Calculate} $x^k = \nabla f(v^k)$,
        \textbf{select} step size $\tau_k > 0$,
        \textbf{update} $v^{k+1} = R_{v^k}(\tau_k x^k)$}
        \EndFor
        \State{\textbf{Return} $\norm{A/B}^2 \approx \tfrac{\norm{A v^k}^2}{\norm{B v^k}^2}$.}
    \end{algorithmic}
\end{algorithm}

For the first-order Riemannian ascent method,
the convergence to critical points for solving \eqref{eq: prob sphere}
can be guaranteed in a sub-linear rate \cite{Lee2012smoothmanifolds}.
Meaning that 
\begin{equation}
    \label{eq: sublinear}
    \min_{k \in \{0,...,n\}} \norm{\grad f(v^k)}^2 \in \mc O(\tfrac{1}{n})
\end{equation}
if $\tau_k = \nicefrac{1}{L}$ and $L \geq \norm{A^{\tT}A}(1 + \kappa(B^{\tT}B))$
where $\kappa(B^{\tT}B) = \lambda_1(B^{\tT}B) / \lambda_{d}(B^{\tT}B)$
is the condition number of $B^{\tT}B \in \mc S_+^d$.
If, additionally, $A^{\tT}A \succ 0$,
i.e. $\rank(A) = d$,
or equivalently $\ker(A) = \{0\}$,
then the linear convergence to the global maximizer can be ensured \cite{alimisis2021distributed}.

\begin{algorithm}
    \caption{Zeroth-order Riemannian gradient ascent method}
    \label{alg: zeroth order}
    \begin{algorithmic}
        \State{\textbf{Given} $A \in \bb R^{m \times d}$ and $B \in \bb R^{\ell \times d}$ such that $\rank(B) = d$.}
        \State{\textbf{Initialize} with $v^0 \in \bb S^{d-1}$ for instance $v^0 = x / \norm{x}$ for $x \sim \mc N(0, I_d)$.}
        \For{$k = 1,2,3,...$}
        \State{\textbf{Sample} $x_i \overset{\text{iid.}}{\sim} \mc N(0, I_d)$ for some $m \in \bb N$.}
        \State{\textbf{Construct} $x^k = \widehat{\grad}_m f(v^k)$ and $\mu_k > 0$ 
        as in \eqref{eq: num grad red}.}
        \State{\textbf{Select} appropriate step size $\tau_k > 0$ and
        \textbf{update} $v^{k+1} = R_{v^k}(\tau_k x^k)$.}
        \EndFor
        \State{\textbf{Return} $\norm{A/B}^2 \approx \tfrac{\norm{A v^k}^2}{\norm{B v^k}^2}$.}
    \end{algorithmic}
\end{algorithm}

For the zeroth-order method,
taking $\tau_k = \nicefrac{1}{2(d+4)L}$
and a square summable scaling sequence,
i.e. $(\mu_k)_{k \in \bb N} \subset \bb R_{> 0}$ 
such that $\sum_{k = 1}^\infty \mu_k^2 < \infty$,
ensures the sublinear convergence rate to critical points \cite{li2023stochastic}.
Notably, 
where there is no guarantee for the convergence to global maximizer at all,
the recent proposed methods \cite{B8,B9,B12}
provably convergence in a sublinear manner as for the first-order method \eqref{eq: sublinear}
especially to the global maximizers.
Here, for the generalized sampling procedure, cf.~Alg.~\ref{alg: main} and ~\ref{alg:czmgRq},
no convergence rate can be proven due to the missing orthogonal construction 
of the step direction, cf.~\eqref{eq: x^k} and~\eqref{eq: tangent surrogate},
and more complicated update scheme, cf.~proof of Prop.~\ref{prop: all conv tau}.

\section{Proofs}\label{sec: app}

\noindent\textbf{Lemma~\ref{lem: lipschitz grad}}
    The (extended) gradient 
    of the objective \eqref{eq: obj}
    is \smash{$\tfrac{20}{\lambda_{d}(B^{\tT}B)^4} \|A\|^2\|B\|^6$}-Lipschitz continuous 
    on  
    $\bb S^{d-1}$. 
\begin{proof}[Proof of Lem.~\ref{lem: lipschitz grad}]
    By \eqref{eq: riemannian gradient}~f. and \eqref{eq: euclidean grad},
    we obtain 
    \begin{align*}
        &\hspace{-20pt}\|\grad f(v) - \grad f(w)\|
        = \|\nabla f(v) - \nabla f(w)\|\\
        & = 2\left\|\frac{\norm{B v}^2 A^{\tT}A v - \norm{A v}^2 B^{\tT}B v}{\norm{B v}^4}
        - \frac{\norm{B w}^2 A^{\tT}A w - \norm{A w}^2 B^{\tT}B w}{\norm{B w}^4}\right\| \\
        & = 2\biggl\|\frac{\norm{B w}^4\norm{B v}^2 A^{\tT}A v - \norm{A v}^2 \norm{B w}^4B^{\tT}B v}{\norm{B v}^4\norm{B w}^4} \\
        & \qquad\qquad - \frac{\norm{B v}^4\norm{B w}^2 A^{\tT}A w - \norm{A w}^2 \norm{B v}^4B^{\tT}B w}{\norm{B v}^4\norm{B w}^4}\biggr\| \\
        & \leq \tfrac{2}{\lambda_{d}(B^{\tT}B)^4} 
        \Bigl[\norm{B v}^2 \norm{B w}^4 \|A^{\tT}A(v - w)\| % \\
        + \norm{A v}^2 \norm{B w}^4 \|B^{\tT}B(v - w)\| \\
        &\qquad\qquad\qquad\quad + \bigl|\norm{B v}^2 \norm{B w}^4 - \norm{B v}^4 \norm{B w}^2\bigr| \norm{A^{\tT}A w} \\
        &\qquad\qquad\qquad\quad + \bigl|\norm{A v}^2 \norm{B w}^4 - \norm{A w}^2 \norm{B v}^4\bigr| \norm{B^{\tT}B w}\Bigl] \\
        & \leq \tfrac{20}{\lambda_{d}(B^{\tT}B)^4}
        \|A\|^2\|B\|^6
        \|v - w\|,
        \qquad\qquad v, w \in \bb S^{d-1}
    \end{align*}
    since 
    \begin{align*}
        \bigl|\norm{B v}^2 \norm{B w}^4 - \norm{B v}^4 \norm{B w}^2\bigr|
        & = \norm{B v}^2 \norm{B w}^2 \underbracket{\bigl|\norm{B w}^2 - \norm{B v}^2\bigr|}_{\leq 2 \norm{B}^2 \norm{v - w}} % \\
        \leq 2 \norm{B}^6 \norm{v - w},
    \end{align*}
    for any $v, w \in \bb S^{d-1}$ and 
    \begin{align*}
        &\bigl|\norm{A v}^2 \norm{B w}^4 - \norm{A w}^2 \norm{B v}^4\bigr|
        \leq \norm{A v}^2 \bigl|\norm{B v}^4 - \norm{B w}^4\bigr|
        + \norm{B v}^4\bigl|\norm{A v}^2 - \norm{A w}^2\bigr| \\
        &\qquad \leq \norm{A v}^2\underbracket{\bigl|\norm{B v}^2 + \norm{B w}^2\bigr|}_{\leq 2 \|B\|^2}
        \cdot \underbracket{\bigl|\norm{B v}^2 - \norm{B w}^2\bigr|}_{\leq 2 \|B\|^2 \|v - w\|} %\\
        + \norm{B v}^4\underbracket{\bigl|\norm{A v}^2 - \norm{A w}^2\bigr|}_{\leq \|A\|^2\|v - w\|} \\
        &\qquad\leq 6 \|A\|^2 \|B\|^4 \norm{v - w},
    \end{align*}
    for any $v, w \in \bb S^{d-1}$.
\end{proof}

\noindent\textbf{Proposition~\ref{prop: as conv eigenspace}}
    Let $\dim(G_{\lambda_1}) < d-1$
    and $(v^k)_{k \in \bb N}$ be the sequence of random variables 
    generated by Alg.~\ref{alg: main}.
    Then there exists a subsequence $(v^{k_j})_{j \in \bb N}$
    and a random variable $\lambda$ a.s. taking values in $\spec((B^{\tT}B)^{-1/2}A^{\tT}A(B^{\tT}B)^{-1/2})$
    such that 
    $\dist(G_\lambda, v^{k_j}) \to 0$ for $j \to \infty$ a.s.
    Moreover,
    the sequence $(\tfrac{a_k}{d_k})_{k \in \bb N}$
    converges to $\lambda$ a.s.
\begin{proof}[Proof of Prop.~\ref{prop: as conv eigenspace}]
    Conclude by the $L^1$-convergence from Cor.~\ref{lem: EE_a_k}
    and the second statement from Cor.~\ref{lem: EE_a_k}
    using the law of total expectation that 
    \begin{equation*}
        \bb E[(\tfrac{\alpha_k}{d_k})^2]
        = \bb E_{v^k \sim V^k}[\bb E_{x^k \sim \mc U(\bb S^{d-1}) \mid V^k = v^k} [(\tfrac{\alpha_k}{d_k})^2]]
        = \tfrac{1}{d} \bb E_{v^k \sim V^k}[d_k^2 \norm{\grad f(v^k)}^2] \to 0,
        \quad k \to \infty.
    \end{equation*}
    Hence,
    there exists a subsequence $(v^{k_j})_{j \in \bb N} \subset \bb S^{d-1}$
    such that 
    \begin{equation*}
        d_{k_j}\norm{\grad f(v^{k_j})} \to 0,
        \quad \text{as} \quad j \to \infty,
        \quad \text{a.s.}
    \end{equation*}
    Due to the boundedness $0 < \lambda_d(B^{\tT}B) \leq d_k \leq \lambda_1(B^{\tT}B)$,
    we obtain 
    \begin{equation*}
        \norm{\grad f(v^{k_j})} \to 0,
        \quad \text{as} \quad j \to \infty,
        \quad \text{a.s.}
    \end{equation*}
    Hence, by construction, cf.~\ref{eq: eigen},
    there exists a sequence of eigenvalues $\lambda_j$ 
    which takes values in the set of the generalized eigenvalues of $(A^{\tT}A, B^{\tT}B)$
    such that 
    \begin{equation*}
        \norm{(A^{\tT}A - \lambda_j B^{\tT}B) v^{k_j}} \to 0,
        \quad \text{as} \quad 
        j \to \infty.
    \end{equation*}
    Therefore,
    we have 
    \begin{equation*}
        a_{k_j}
        = \scp{v^{k_j}}{A^{\tT}A v^{k_j}}
        = \underbracket{\scp{v^{k_j}}{(A^{\tT}A - \lambda_j B^{\tT}B) v^{k_j}}}_{\to 0, \quad j \to \infty} + \underbracket{\scp{v^{k_j}}{\lambda_j B^{\tT}B v^{k_j}}}_{ = \lambda_j d_{k_j}}
    \end{equation*}
    such that by Cor.~\ref{cor: monoton conv} we obtain
    \begin{align*}
        \lim_{k \to \infty} f(v^k)
        &= \lim_{j \to \infty} f(v^{k_j})
        = \lim_{k \to \infty} \frac{a_{k}}{d_{k}} \\
        &= \lim_{j \to \infty} \frac{a_{k_j}}{d_{k_j}}
        = \lim_{j \to \infty} \lambda_j
        =: \lambda \in \spec((B^{\tT}B)^{-1/2}A^{\tT}A (B^{\tT}B)^{-1/2}).
    \end{align*}
    Since $\bb S^{d-1}$ is compact,
    there exists a convergent subsequence $(v^{k_{j_\ell}})_{\ell \in \bb N} \subset \bb S^{d-1}$
    with limit $v \in \bb S^{d-1}$ such that 
    \begin{equation*}
        \lim_{\ell \to \infty} \norm{(A^{\tT}A - \lambda_{j_\ell} B^{\tT}B) v^{k_{j_\ell}}}
        = \norm{(A^{\tT}A - \lambda B^{\tT}B) v} = 0
    \end{equation*}
    and hence $(v, \lambda)$ is a generalized eigen pair of $(A^{\tT}A, B^{\tT}B)$.
    Finally, we conclude by 
    \begin{equation*}
        \norm{(A^{\tT}A - \lambda B^{\tT}B) v^{k_j}}
        \leq \norm{(A^{\tT}A - \lambda_j B^{\tT}B) v^{k_j}} + |\lambda - \lambda_j| \cdot \norm{B^{\tT}B v^{k_j}}
        \to 0, \quad \text{as} \quad j \to \infty,
    \end{equation*}
    such that $\dist(G_\lambda, v^{k_j}) \to 0$ as $j \to \infty$ a.s.
\end{proof}

\noindent\textbf{Lemma~\ref{lem: uniform lower bound}}
    Let $v, \tilde v \in \bb S^{d-1}$ and $\varepsilon > 0$. 
    Define 
    \begin{align*}
        \mc D_v \coloneqq \left\{ x \in \bb S^{d-1} 
        \;\middle|\; 
        \exists \tau \in \bb R, 
        R_v(\tau x) 
        = \tfrac{v + \tau x}{\norm{v + \tau x}} \in \bb B_\varepsilon(\tilde v) \cup \bb B_\varepsilon(-\tilde v)\right\}.
    \end{align*}
    There exists some $p_{\varepsilon,d} > 0$ 
    such that $\inf_{v \in \bb S^{d-1}} \sigma_{d-1}(\mc D_v) > p_{\varepsilon,d}$.
\begin{proof}[Proof of Lem.~\ref{lem: uniform lower bound}]
    W.l.o.g assume that $\scp{v}{\tilde v} \geq 0$, 
    otherwise consider $-\tilde v$.
    Hence it holds $\norm{v - \tilde v} \leq \sqrt{2}$.
    Furthermore, if $\norm{v - \tilde v} < \varepsilon$, it suffices for any $x \in \bb S^{d-1}$
    to take $\tau = 0$ such that $\sigma_{d-1}(\mc D_v) = 1$.
    Now, 
    since for any $y \in \bb S^{d-1}$ and $w \in \bb R^d\setminus\{0\}$ holds that  
    \begin{align}
        \label{eq: uniform lower bound}
        \norm[\Big]{\tfrac{w}{\norm{w}} - y}
        &\leq \norm[\Big]{\tfrac{w}{\norm{w}} - w} + \norm{w - y}
        = \abs[\Big]{\tfrac{1}{\norm{w}} - 1} \norm{w} + \norm{w - y} \notag \\
        &= \abs[\big]{1 - \norm{w}} + \norm{w - y} 
        = \abs[\big]{\norm{y} - \norm{w}} + \norm{w - y} % \notag \\
        \leq 2 \norm{w - y},
    \end{align}
    it suffices to take 
    \begin{equation*}
        \tilde{\mc D}_v \coloneqq \{x \in \bb S^{d-1} \mid \exists \tau \in \bb R, v + \tau x \in \bb B_{\nicefrac{\varepsilon}{2}}(\tilde v) \cup \bb B_{\nicefrac{\varepsilon}{2}}(-\tilde v)\}
        \subset \mc D_v.
    \end{equation*}
    As the latter can be trivially rewritten 
    \[
        \tilde{\mc D}_v = \{x \in \bb S^{d-1} \mid \exists \tau \in \bb R, \tau x \in \bb B_{\nicefrac{\varepsilon}{2}}(\tilde v - v) \cup \bb B_{\nicefrac{\varepsilon}{2}}(v+\tilde v)\}
    \]
    it includes a \textit{hyperspherical cap} $\mc K_\varepsilon \subset \tilde{\mc D}_v$ \cite{li2011concise} with opening angle 
    \[
        \tfrac{1}{2} \geq \sin(\alpha_\varepsilon) = \frac{\nicefrac{\varepsilon}{2}}{\norm{v - \tilde v}} \geq \tfrac{\varepsilon}{4\sqrt{2}} =: \sin(\beta_\varepsilon).
    \]
    An other hyperspherical cap $\tilde{\mc K}_\varepsilon \subset \mc K_\varepsilon$ is included
    defined by the opening angle $\beta_\varepsilon$.
    The surface area is given by the \textit{incomplete Beta-function} \cite{li2011concise}
    such that by the monotonicity holds
    \begin{align*}
        \sigma_{d-1}(\mc D_v)
        &\geq \sigma_{d-1}(\tilde{\mc D}_v)
        \geq \sigma_{d-1}(\mc K_\varepsilon)
        \geq \sigma_{d-1}(\tilde{\mc K}_\varepsilon)
        = \mathrm{B}(\sin(\beta_\varepsilon), \tfrac{d-1}{2}, \tfrac{1}{2}) \\
        &= \int_0^{\sin(\beta_\varepsilon)} t^{\tfrac{d-3}{2}}(1 - t)^{-\tfrac{1}{2}} \; \mathrm{d} t 
        \geq \int_0^{\sin(\beta_\varepsilon)} t^{\tfrac{d-3}{2}} \; \mathrm{d} t 
        = \tfrac{2}{d-1}\bigl(\tfrac{\varepsilon}{2\sqrt{2}}\bigr)^{\tfrac{d-1}{2}}
        \eqqcolon p_{\varepsilon,d},
    \end{align*}
    using that $(1-t)^{-1/2}\geq 1$ for $0\leq t\leq 1$
    in the last inequality.
\end{proof}

\noindent\textbf{Proposition~\ref{prop: rie hess}}
    Let $A \in \bb R^{d \times d}$.
    It holds
    \begin{equation*}
        \bb E_{x \sim \mc U(\bb S^{d-1})}[\scp{x}{Ax}] = \frac{\trace(\symA)}{d} 
        \quad\text{and}\quad
        \bb E_{x \sim \mc U(\bb S^{d-1})}[\scp{x}{Ax} xx^{\tT}] = \frac{2\symA + \trace(A)I_d}{d(d+2)}.
    \end{equation*}
\begin{proof}[Proof of Prop.~\ref{prop: rie hess}]
    For the first assertion,
    it holds 
    \begin{equation}
        \label{eq: symA inner}
        \scp{x}{Ax}
        = \frac{1}{2}(\scp{x}{Ax} + \langle A^{\tT}x, x\rangle)
        = \langle x, \underbracket{\tfrac{1}{2}(A + A^{\tT})}_{=: \symA} x\rangle
        = \scp{x}{\symA x}
        = \trace(\symA xx^{\tT}).
    \end{equation}
    Hence, 
    by the linearity of the trace,
    we have 
    \begin{equation*}
        \bb E_{x \sim \mc U(\bb S^{d-1})}[\scp{x}{Ax}]
        = \bb E_{x \sim \mc U(\bb S^{d-1})}[\trace(\symA xx^{\tT})]
        = \trace(\symA \bb E_{x \sim \mc U(\bb S^{d-1})}[xx^{\tT}])
        = \frac{1}{d} \trace(\symA),
    \end{equation*}
    using \eqref{eq: x^k}~f.
    %
    For the second assertion 
    by utilizing that the mapping 
    \begin{equation*}
        \mc M : \mc S^d \to \mc S^d,
        \quad 
        C \mapsto \bb E_{x \sim \mc U(\bb S^{d-1})}[\scp{x}{Cx}xx^{\tT}]
    \end{equation*}
    is orthogonal equivariant, 
    which means that 
    \begin{align*}
        \mc M(Q^{\tT} C Q)
        &= \bb E_{x \sim \mc U(\bb S^{d-1})}[\scp{x}{Q^{\tT} C Q x} x x^{\tT}] 
        = \bb E_{x \sim \mc U(\bb S^{d-1})}[\scp{Q x}{C Q x} Q^{\tT}Q x (Q^{\tT}Q x)^{\tT}] \\
        &= \bb E_{x \sim \mc U(\bb S^{d-1})}[\scp{x}{C x} Q^{\tT} x x^{\tT} Q] 
        = Q^{\tT} \bb E_{x \sim \mc U(\bb S^{d-1})}[\scp{x}{C x} x x^{\tT}] Q \\
        &= Q^{\tT} \mc M(C) Q,
    \end{align*}
    holds by Schur's lemma \cite[§~1.2]{fulton2004representation} 
    and by the decomposition 
    of the set of Hermitian matrices 
    \begin{equation*}
        \mc S^d = \spa(I_d) \oplus \{C \in \mc S^d : \trace(C) = 0\}
    \end{equation*}
    that some parameters $\varkappa_1, \varkappa_2 \in \bb R$ exist
    such that
    \begin{equation*}
        \mc M(C) = \varkappa_1 C + \varkappa_2 \trace(C) I_d.
    \end{equation*}
    Furthermore,
    by Isserlis--Wick's theorem \cite{Isserlis1918,Wick1950}
    holds, by \eqref{eq: x^k}~f., with 
    \begin{equation*}
        \mc M(I_d) 
        = \bb E_{x \sim \mc U(\bb S^{d-1})}[xx^{\tT}] 
        = \tfrac{1}{d} I_d 
        = \varkappa_1 I_d + \varkappa_2 d I_d
    \end{equation*}
    and $\mc M(e_1e_1^{\tT}) = \bb E_{x \sim \mc U(\bb S^{d-1})}[x_1^2 x x^{\tT}]$
    from the $(1,1)$- and $(1,2)$-entry 
    that
    \begin{equation*}
        \bb E_{x \sim \mc U(\bb S^{d-1})}[x_1^4] 
        = \frac{3}{d(d+2)},
        \quad \text{and} \quad 
        \bb E_{x \sim \mc U(\bb S^{d-1})}[x_1^2 x_2^2] = \frac{1}{d(d+2)}.
    \end{equation*}
    Hence,
    by symmetry reasons holds 
        $\mc M(e_1 e_1^{\tT})
        = \tfrac{1}{d(d+2)} 
        \diag(3,1,..,1)
        = \varkappa_1 e_1 e_1^{\tT} + \varkappa_2 I_d$.
    Comparing the first two diagonal entries 
    in the latter equation 
    yields 
    \begin{equation*}
        \varkappa_1 + \varkappa_2 = \frac{3}{d(d+2)},
        \quad \varkappa_2 = \frac{1}{d(d+2)},
        \quad\text{such that}\quad
        \varkappa_1 = \frac{2}{d(d+2)},
        \quad \varkappa_2 = \frac{1}{d(d+2)}.
    \end{equation*}
    Applying all this onto $\symA$ due to \eqref{eq: symA inner}
    yields the assertion.
\end{proof}


\noindent\textbf{Corollary~\ref{cor: riemannian hessian estimator}}
    Let $A \in \bb R^{m \times d}$ and $B \in \bb R^{\ell \times d}$
    It holds 
    \begin{align*}
        \bb E_{x \sim \mc U(\bb S^{d-1})}
        \Bigl[\bigl(\norm{A x}^2 - f(v)\norm{B x}^2\bigr)(xx^{\tT} - \tfrac{1}{d+2} I_d)\Bigr]
        = \frac{2}{d(d+2)} H(v).
    \end{align*}
    and 
    \begin{align*}
        \bb E_{y \sim \mc U(\bb T_v \cap \bb S^{d-1})}
        \Bigl[\bigl(\norm{A y}^2 - f(v)\norm{B y}^2\bigr)(yy^{\tT} - \tfrac{1}{d+1} P_v)\Bigr] % \\
        &= \frac{\norm{B v}^2}{(d-1)(d+1)} \hess f(v).
    \end{align*}
\begin{proof}[Proof of Cor.~\ref{cor: riemannian hessian estimator}]
    The first assertion is a direct consequence of Prop.~\ref{prop: rie hess}.
    For the second assertion,
    utilize \eqref{eq: tangent surrogate} 
    with $\bb E_{y \sim \mc U(\bb T_v \cap \bb S^{d-1})}[yy^{\tT}] 
    = \tfrac{1}{d-1}(I_d - vv^{\tT}) 
    = \tfrac{1}{d-1} P_v$ \cite[Lem.~4.1]{B9}
    and for some $C \in \bb R^{d \times d}$ that holds
    \begin{equation*}
        \bb E_{y \sim \mc U(\bb T_v \cap \bb S^{d-1})}[\scp{y}{Cy}] 
        = \tfrac{1}{d-1}\trace(P_v \symC P_v)
    \end{equation*}
    according to Prop.~\ref{prop: rie hess}.
    Furthermore holds 
    \begin{equation*}
        \bb E_{y \sim \mc U(\bb T_v \cap \bb S^{d-1})}[\scp{y}{Cy}yy^{\tT}]
        = \tfrac{1}{(d-1)(d+1)}\bigl(2 P_v \symC P_v + \trace(P_v \symC P_v) P_v\bigr).
    \end{equation*}
    Plugging in $C = H(v) = (A^{\tT}A - f(v) B^{\tT}B) \in \mc S^d$ from \eqref{eq: riemannian hess special}
    yields the assertion. 
\end{proof}

\end{document}

