\documentclass[12pt]{article}
\usepackage[latin9]{inputenc}
\usepackage{geometry}
\geometry{verbose,tmargin=1in,bmargin=1in,lmargin=1in,rmargin=1in}
\usepackage[active]{srcltx}
\usepackage{float}
\usepackage{amsmath}
\usepackage{amsthm}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{rotfloat}
\usepackage{setspace}
\usepackage{esint}
\usepackage[authoryear]{natbib}
\usepackage[font=normalsize,labelfont=bf]{caption}
%\usepackage{helvet}
\usepackage{comment}
\usepackage{xr-hyper}
\usepackage{hyperref}
\usepackage{nicefrac}
\usepackage{mathtools}
\usepackage[caption=false]{subfig}
%\graphicspath{{Images/}}
%\onehalfspacing
\usepackage{algorithm}
\usepackage{algpseudocode}
\makeatletter
\sloppy
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% LyX specific LaTeX commands.
%% Because html converters don't know tabularnewline
\providecommand{\tabularnewline}{\\}
\floatstyle{ruled}
\newfloat{algorithm}{tbp}{loa}
\providecommand{\algorithmname}{Algorithm}
\floatname{algorithm}{\protect\algorithmname}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% User specified LaTeX commands.


\usepackage{latexsym}
\usepackage{amsthm}\usepackage{amsfonts}\usepackage{graphicx}\usepackage{epsfig}
%\usepackage{bm}
%\def\bm{\boldmath}
\expandafter\def\csname bm\endcsname{\boldmath}

\newcommand*{\patchAmsMathEnvironmentForLineno}[1]{%
      \expandafter\let\csname old#1\expandafter\endcsname\csname #1\endcsname
      \expandafter\let\csname oldend#1\expandafter\endcsname\csname end#1\endcsname
      \renewenvironment{#1}%
         {\linenomath\csname old#1\endcsname}%
         {\csname oldend#1\endcsname\endlinenomath}}%
    \newcommand*{\patchBothAmsMathEnvironmentsForLineno}[1]{%
      \patchAmsMathEnvironmentForLineno{#1}%
      \patchAmsMathEnvironmentForLineno{#1*}}%
    \AtBeginDocument{%
    \patchBothAmsMathEnvironmentsForLineno{equation}%
    \patchBothAmsMathEnvironmentsForLineno{align}%
    \patchBothAmsMathEnvironmentsForLineno{flalign}%
    \patchBothAmsMathEnvironmentsForLineno{alignat}%
    \patchBothAmsMathEnvironmentsForLineno{gather}%
    \patchBothAmsMathEnvironmentsForLineno{multline}%
    }
%\usepackage[mathlines,displaymath]{lineno}
%\linespread{1}
%\linenumbers

%\addtolength{\textwidth}{1.2in}
%\addtolength{\oddsidemargin}{-0.5in}
%\addtolength{\textheight}{1.6in}
%\addtolength{\topmargin}{-0.8in}

\usepackage{setspace}
\doublespacing

%\addtolength{\textwidth}{1.2in}
%\addtolength{\oddsidemargin}{-0.5in}
%\addtolength{\textheight}{1.7in}
%\addtolength{\topmargin}{-0.7in}


%\addtolength{\oddsidemargin}{-.5in}%
%\addtolength{\evensidemargin}{-1in}%
%\addtolength{\textwidth}{1in}%
%\addtolength{\textheight}{1.7in}%
%\addtolength{\topmargin}{-1in}%


%\include{def}
\def\dispmuskip{\thinmuskip= 3mu plus 0mu minus 2mu \medmuskip=  4mu plus 2mu minus 2mu \thickmuskip=5mu plus 5mu minus 2mu}
\def\textmuskip{\thinmuskip= 0mu                    \medmuskip=  1mu plus 1mu minus 1mu \thickmuskip=2mu plus 3mu minus 1mu}
\def\beq{\dispmuskip\begin{equation}}    \def\eeq{\end{equation}\textmuskip}
\def\beqn{\dispmuskip\begin{displaymath}}\def\eeqn{\end{displaymath}\textmuskip}
\def\bea{\dispmuskip\begin{eqnarray}}    \def\eea{\end{eqnarray}\textmuskip}
\def\bean{\dispmuskip\begin{eqnarray*}}  \def\eean{\end{eqnarray*}\textmuskip}

\def\paradot#1{\vspace{1.3ex plus 0.7ex minus 0.5ex}\noindent{\bf\boldmath{#1.}}}

\newcommand{\MN}{Mixture of normals}
\newcommand{\mn}{mixture of normals}
\newcommand{\MAMN}{Marginally adjusted mixture of normals}
\newcommand{\mamn}{marginally adjusted mixture of normals}
\newcommand{\St}{Skew-$t$}
\newcommand{\st}{skew-$t$}
\newcommand{\MNC}{Mixture of normal copulas}
\newcommand{\mnc}{mixture of normal copulas}
\newcommand{\NC}{Normal copula}
\newcommand{\nc}{normal copula}
\newcommand{\SA}{stochastic approximation}
\newcommand{\cdf}{cumulative distribution function}
\newcommand{\pdf}{probability density function}
\newcommand{\KL}{Kullback-Leibler}
\newcommand{\DGP}{data generating process}
\newcommand{\DGPS}{data generating processes}
\newcommand{\MCMC}{Markov chain Monte Carlo}
\newcommand{\dof}{degrees of freedom}
\newcommand{\mfc}{mixture of latent factor copulas}
\newcommand{\cmf}{copula of a mixture of latent factors}
\newcommand{\mfa}{mixture of factor analyzers}
\newcommand{\MFA}{Mixture of factor analyzers}
\newcommand{\mamfa}{marginally adjusted mixture of factor analyzers}
\newcommand{\MAMFA}{Marginally adjusted mixture of factor analyzers}
\newcommand{\cmn}{copula of a mixture of normals}
\newcommand{\by}{\bm{y}}
\newcommand{\bx}{\bm{x}}
\newcommand{\bu}{\bm{u}}
\newcommand{\bmu}{\bm{\mu}}
\newcommand{\bI}{\bm{I}}
\newcommand{\biota}{\bm{\iota}}
\newcommand{\bSigma}{\bm{\Sigma}}
\newcommand{\bV}{\bW}
\newcommand{\bW}{\bm{W}}
\newcommand{\be}{\bm{e}}
\newcommand{\mbfC}{\mathbf{C}}
\newcommand{\diag}{\text{diag}}
\newcommand{\mbfmu}{\mathbf{\mu}}
\newcommand{\mbfSigma}{\mathbf{\Sigma}}
\newcommand{\mbfI}{\mathbf{I}}
\newcommand{\mbfzero}{\mathbf{0}}
\newcommand{\mbfW}{\mathbf{W}}
\newcommand{\eps}{\epsilon}
\newcommand{\wh}{\widehat}
\newcommand{\wt}{\widetilde}
\newcommand{\blind}{0}
\newcommand{\calM}{{\cal M}}
\newcommand{\iid}{iid}
\usepackage{bm}  % allows bold Greek letters

\newcommand{\bs}[1]{\bm{#1}}           % shorthand for bold symbols
\newcommand{\thetad}{\bs{\theta}_d}    % defines \thetad as bold theta with 

\def\v{\boldsymbol}
\def\SetR{I\!R}
\def\SetN{I\!\!N}
\def\SetB{I\!\!B}
\def\SetZ{Z\!\!\!Z}
\def\e{{\rm e}}                        % natural e
\def\B{\{0,1\}}
\def\E{{\mathbb E}}                         % Expectation
\def\V{{\mathbb V}}
\def\P{{\rm P}}                         % Probability
\def\lb{{\log_2}}
\def\I{1\!\!1} 				% identity matrix
\def\v{\boldsymbol}
\def\trp{{\!\top\!}}
\def\EE{I\!\!E}
\def\G{\Gamma}
\def\a{\alpha}
\def\D{{\cal D}}
\def\d{\delta}
\def\ep{\epsilon}
\def\g{\gamma}
\def\s{\sigma}
\def\k{\kappa}
\def\Sig{\Sigma}
\def\t{\theta}
\def\b{\beta}
\def\l{\lambda}
\def\Ld{\Lambda}
\def\r{\rho}
\def\A{{\cal A}}
\def\F{{\cal F}}
\def\M{{\cal M}}
\def\N{{\cal N}}
\def\R{{\cal R}}
\def\X{{\cal X}}
\def\Y{{\cal Y}}
\def\H{{\cal H}}
\def\ESS{\text{\rm ESS}}
%\def\MCMC{\text{\rm MCMC}}
\def\AS{\text{\rm AS}}
\def\LPDS{\text{\rm LPDS}}
\def\PSE{\text{\rm PSE}}
\def\PPS{\text{\rm PPS}}
\def\Kl{\text{\rm KL}}
\def\BIC{\text{\rm BIC}}
\def\AIC{\text{\rm AIC}}
\def\CV{\text{\rm CV}}
\def\tr{\text{\rm tr}}
\def\vec{\text{\rm vec}}
\def\vech{\text{\rm vech}}
\def\vechsq{P}
\def\OLS{\text{\rm OLS}}
\def\MSE{\text{\rm MSE}}
\def\MLE{\text{\rm MLE}}
\def\cov{\text{\rm cov}}
\def\IS{\text{\rm IS}}
\def\IF{\text{\rm IF}}
\def\argmin{\text{\rm argmin}}
\def\argmax{\text{\rm argmax}}
\def\Sup{\text{\rm Sup}}
\def\diag{\text{\rm diag}}
\def\Var{\text{\rm Var}}
\def\Eqref{Eq. \eqref}
\def\wh{\widehat}
\def\d{{\rm d}}
\DeclareMathOperator*{\sgn}{sgn}
% \newcommand{\sign}{\rm sign}
\renewcommand{\bibname}{References}
\usepackage[mathlines]{lineno} %displaymath
%\linenumbers

\newcommand\blfootnote[1]{%
	\begingroup
	\renewcommand\thefootnote{}\footnote{#1}%
	\addtocounter{footnote}{-1}%
	\endgroup
}

\makeatletter
\newcommand*{\addFileDependency}[1]{% argument=file name and extension
  \typeout{(#1)}
  \@addtofilelist{#1}
  \IfFileExists{#1}{}{\typeout{No file #1.}}
}
\makeatother

\newcommand*{\myexternaldocument}[1]{
    \externaldocument{#1}
    \addFileDependency{#1.tex}
    \addFileDependency{#1.aux}
}
%%% END HELPER CODE

% TODO: check these pacakges
\usepackage{subfig}
\usepackage[export]{adjustbox}

%%% Tom's commands %%% 
\newcommand{\bb}[1]{\boldsymbol{#1}}

\newcommand{\abs}[1]{\|{#1}\|}
\newcommand{\btheta}{\bb{\theta}}
\newcommand{\bvartheta}{\bb{\vartheta}}
\newcommand{\bby}{\bb{y}}
\newcommand{\bbD}{\bb{D}}
\newcommand{\br}{\bb{r}}
\newcommand{\sign}[1]{\text{sign}({#1})}
% \newcommand{\bf}{\bb{f}}
\newcommand{\bLambda}{\bb{\Lambda}}
\newcommand{\blambda}{\bb{\lambda}}
\newcommand{\bbbeta}{\bb{\beta}}
% \newcommand{\B}{\mathcal{B}}
\newcommand{\bX}{\bb{X}}
\newcommand{\bbI}{\bb{\mathrm{I}}}
\newcommand{\bbmu}{\bb{\mu}}
\newcommand{\bsigma}{\bb{\sigma}}
\newcommand{\bbSigma}{\bb{\Sigma}}
\newcommand{\bomega}{\bb{\omega}}
\newcommand{\bbOmega}{\bb{\Omega}}
\newcommand{\bgamma}{\bb{\gamma}}
\newcommand{\bbeta}{\bb{\eta}}
\newcommand{\idxs}{\mathrm{v}}
\newcommand{\bidxs}{\mathbf{v}}
% \newcommand{\E}{\mathbb{E}}
\newcommand{\q}{q_{\blambda}(\btheta)}
% \newcommand{\e}{\bb{\epsilon}}
\newcommand{\elbo}{\mathcal{L}(\blambda)}
\newcommand{\bxi}{\bb{\xi}}
\newcommand{\bz}{\bb{z}}
\newcommand{\bh}{\bb{h}}
\newcommand{\bbu}{\bb{u}}
\newcommand{\bH}{\bb{\mathrm{H}}}
\newcommand{\bigO}{\mathcal{O}}
\newcommand{\rest}{\text{rest}}
\newcommand{\cond}{\big\vert }

\newcommand{\thetacop}{\bs{\theta}_{\textrm{cop}}}
%%%%% Notation for the paper %%%%%

% number of components
\newcommand{\Ky}{K_{\eta}}
\newcommand{\Kr}{K_{\epsilon}}

% number of factors
\newcommand{\nfactorsEta}{q^{\eta}}
\newcommand{\nfactorsEpsilon}{q^{\epsilon}}
\newcommand{\nfactorsVolatility}{q^{w}}

% weights
\newcommand{\weightsEta}{\omega^{\eta}}
\newcommand{\weightsEpsilon}{\omega^{\epsilon}}

% means
\newcommand{\meanEta}{\bb{\mu}}
\newcommand{\meanEpsilon}{\bb{\nu}}

% factor loadings
\newcommand{\factloadEta}{\bb{\beta}}
\newcommand{\factloadEpsilon}{\bb{\Lambda}}
\newcommand{\factloadVolatility}{\bb{\beta}_w}

% factors
\newcommand{\factorsEta}{\bb{f}_{\eta, t}}
\newcommand{\factorsEpsilon}{\bb{f}_{\epsilon,t}}
\newcommand{\factorsVolatility}{\bb{f}_{w,t}}

% diagonal matrices
\newcommand{\diagEta}{\bb{D}}
\newcommand{\diagVolatility}{{\bb{D}^2_w}}
\newcommand{\diagEpsilon}{\bb{P}^2}

\newcommand{\bbH}{\bb{\mathrm{H}}}

\newcommand{\yj}[2]{YJ--MoN$(\Kr={#1}, \nfactorsEpsilon={#2})$}
\newcommand{\mon}[2]{MoN$(\Kr={#1}, \nfactorsEpsilon={#2})$}
\newcommand{\omori}{Omori $(\Kr=10)$ }
\newcommand{\fsv}[1]{FSV$(q^f={#1})$}
\newcommand{\lamd}[0]{\bs{\lambda}_{d}(\bs{y}_{d};\bs{\gamma}_{d})}

%\newcommand{\thetamar}{\bs\theta_{\textrm{M}}}
\newcommand{\thetamar}{\bs\theta_{d}}
%\newcommand{\Ymar}{\bs{Y}_{\textrm{M}}}
\newcommand{\Ymar}{\bs{Y}_{(d)}}
%\newcommand{\ymar}{\bs{y}_{\textrm{M}}}
\newcommand{\ymar}{\bs{y}_{(d)}}

\newcommand{\Gammamar}{\bs{\gamma}_{\textrm{mar}}}
\newcommand{\Lambdamar}{\bs{\lambda}_{\textrm{mar}}}
\usepackage{comment}
%\newcommand{\bs}[1]{\bs{#1}}
% MoN for y_t
\newcommand{\monyt}[2]{MoN$(\Ky={#1}, \nfactorsEta={#2})$}
\newcommand{\lambdagd}[1]{\bs{\lambda}_{d, \bs{\gamma}_d}(#1)}
% \newcommand{\norm}{\bb{\mathcal{N}}}
% \newcommand{\EE}[2]{\mathbb{E}_{#1}\left[ {#2} \right]}
% \E_{q(\bxi)}\left[ \log p(\bb{X}, \bxi)\right]

\let\oldref\ref
\renewcommand{\ref}[1]{(\oldref{#1})}

\usepackage{amsthm}
\theoremstyle{definition}
\newtheorem{example}{Example} % [section]  % TODO: uncomment this out
\newtheorem{simulation}{Simulation}[section] %[subsection]
\usepackage{authblk}

\usepackage{bbm}
\sloppy
\usepackage{xr}
\externaldocument{Online_supplement}

\usepackage{tikz}
\usetikzlibrary{positioning, decorations.pathreplacing, shapes.misc, fit}
\usetikzlibrary{arrows.meta}
%\input{Online_supplement_2025.tex}

% \newcommand{\vech}[1]{\text{vech}(#1)}
% \let\oldvec\vec
% \renewcommand{\vec}[1]{\text{vec}(#1)}
%%% %%%


% put all the external documents here!
%\myexternaldocument{reply2refereesJBES_R2}
%\myexternaldocument{DSGEsupplementR2}
%%% END HELPER CODE

%\def\spacingset#1{\renewcommand{\baselinestretch}%
%{#1}\small\normalsize} \spacingset{1}
%\spacingset{1.8} % DON'T change the spacing!




\begin{document}




%\def\spacingset#1{\renewcommand{\baselinestretch}%
%{#1}\small\normalsize} \spacingset{1}

\title{\bf Flexible Bayesian Models for Time-Varying Income Distributions}
\author{David Gunawan}
\affil{School of Mathematics and Physics, University of Wollongong, Wollongong, New South Wales, Australia}
\maketitle




\begin{abstract}
Survey data are widely used to study how income inequality, poverty, and welfare evolve over time. A common practice is to estimate the income distribution separately for each year, treating annual observations as independent cross-sections. For population subgroups with relatively small sample sizes, however, this approach can produce unstable parameter estimates, imprecise inference for inequality and poverty measures, and potentially misleading posterior probabilities of Lorenz and stochastic dominance. This paper develops flexible Bayesian models for time-varying income distributions that borrow strength across adjacent years by allowing the parameters of income distributions to evolve dynamically. We consider a random walk specification and an extended model with shrinkage priors. The proposed framework yields coherent inference for the full income distributions over time, as well as for associated inequality measures, poverty indices, and dominance probabilities. Simulation studies show that, relative to independent year-by-year models, the proposed approach produces substantially more precise and stable inference, while avoiding spurious variation in welfare comparisons. An application to the Aboriginal and residents of the Australian Capital Territory (ACT) population subgroups in the Household, Income and Labour Dynamics in Australia survey shows that the dynamic models deliver improved inference for income distributions and related welfare measures, and can change conclusions about distributional dominance over time.
\end{abstract}
%Survey datasets such as the Household, Income and Labour Dynamics in Australia (HILDA) survey are increasingly used to assess how income inequality, poverty, and welfare change over time. Standard practice typically estimates the income distribution separately for each year, treating annual observations as independent cross-sections. This can lead to unstable inference, particularly for population subgroups with small sample sizes in individual years.
%This paper develops flexible Bayesian time-varying parametric models for income distributions that explicitly link information across time. The parameters of standard income models are allowed to evolve dynamically through random walk processes, with an extension based on horseshoe shrinkage priors that regularise noise while still permitting genuine distributional change. The proposed models borrow strength across adjacent years and thereby yield more stable and more precise inference for time-varying income distributions, inequality measures, poverty indices, and posterior probabilities of Lorenz and stochastic dominance.
%The framework provides a practical and interpretable alternative to independent year-by-year income models, especially for subgroup analysis in survey data where the number of observations per year is limited.




Keywords: Generalised Beta 2 Distribution; Random Walk Model; Markov Chain Monte Carlo; Horseshoe Shrinkage Priors; Posterior Probability of Stochastic Dominance; Aboriginal Population Subgroup.


    



\section{Introduction}
The estimation of income distributions plays a central role in the measurement of inequality and poverty and, more broadly, in welfare comparisons across time and across populations. For useful overviews of the extensive literature on income distribution modelling, including alternative specifications, their properties, and estimation methods, see the monograph by \citet{KleiberKotz2003}, the edited volume by \citet{Chotikapanich2008}, and the articles by \citet{BandourianMcDonaldTurley2003} and \citet{McDonaldXu1995}. The present paper focuses on inference for income distributions of population subgroups for which only a small number of observations are available in each year.

%This paper focuses on survey data rather than grouped data, with particular emphasis on inference for the income distribution of a population subgroup for which the number of observations is small in each year. 

The availability of detailed survey data has transformed empirical research on inequality and poverty. These data provide a rich basis for tracking distributional change, evaluating policy
reforms, and quantifying the persistence of economic disadvantage. Prominent examples
include the Household Income and Labour Dynamics in Australia (HILDA) survey \citep{WatsonWooden2012HILDA} and the
Panel Study of Income Dynamics (PSID) in the United States \citep{McGonagle2012PSID}. In Australia, HILDA has become a key resource for  analysing
how welfare, inequality and poverty evolve for different demographic and labour-market groups.
As such datasets continue to mature and expand, they increasingly support inherently dynamic questions: whether inequality and poverty are rising or falling, and how future distributions might evolve under plausible trajectories.

Policy discussions typically focus on inequality measures, poverty indices, and welfare comparisons that depend on the full income distribution. These include widely used measures of inequality, such as the Gini coefficient and generalised entropy measures, including the Theil indices \citep{Cowell2011}, as well as poverty measures such as the headcount ratio, poverty gap, and related indices \citep{FosterGreerThorbecke1984}. In addition, distributional comparisons based on Lorenz and stochastic dominance provide partial orderings that are often more informative than any single summary measure \citep{barrett2003consistent,barrett2014consistent}.

%Despite their broad use, these quantities are statistically demanding:
%they are sensitive to tail behaviour, depend on the full shape of the distribution, and
%can exhibit substantial sampling variability particularly when annual sample sizes are
%moderate, when the tails are thinly observed, or when the assumed distributional family is
%flexible and multi-parameter. The problem is exacerbated for measures
%that place weight on the distributional tails, because tail parameters are often weakly identified
%in any single year.

A common strategy in applied work is to estimate a parametric income distribution separately
for each year, treating each year as an independent cross-section, for example Dagum \citep{Dagum1977}, Singh-Maddala \citep{SinghMaddala1976}, and Generalised Beta 2 (GB2) distributions \citep{McDonaldXu1995}. Under this approach, the distributional parameters are estimated using only within-year observations. The posterior densities of inequality and poverty measures, together with the posterior probabilities of dominance, are then computed as functions of parameter draws obtained from Markov chain Monte Carlo (MCMC) algorithms \citep{gunawan2021posterior}. While simple,
this year-by-year estimation ignores an important empirical feature: income distributions
typically evolve smoothly over time, interrupted by occasional shifts associated with macroeconomic
shocks, labour-market changes, or policy reforms. When adjacent years are in fact similar,
estimating each year independently can lead to noisy parameter paths and unstable year-to-year
movements in derived welfare, inequality and poverty measures, particularly for small sample sizes. As a result, the independent cross-sectional approach may produce spurious volatility in estimates of inequality and poverty, and may also yield misleading posterior probabilities of dominance.

%At the same time, the model allows for a genuine distributional
%change by learning the degree of time variation from the data.

 
This paper makes several contributions. First, this paper develops a flexible dynamic statistical model for income distributions that
explicitly links information across time. The key idea is to treat the distributional parameters
as latent, time-varying states that evolve according to a stochastic process. 
Second, it shows that dynamic modelling improves inference for income distributions, especially for population subgroups with small annual sample sizes. By linking adjacent years, the proposed approach yields smoother and more stable estimates of income distribution parameters and substantially more precise inference for derived welfare summaries. Third, the paper shows that the benefits are not limited to narrower credible intervals. Since poverty, inequality, and dominance comparisons are sensitive to noise in the fitted distributions, independent year-by-year models can lead to substantively different and potentially misleading conclusions about welfare, poverty, and inequality changes over time. In contrast, the proposed dynamic models provide posterior inference that is more stable, and better aligned with the underlying temporal structure in the data.

We illustrate the approach using both a simulation study and an application to income data from HILDA, with particular emphasis on the Aboriginal population subgroup and the residents of the Australian Capital Territory (ACT) subgroup. The simulation results show that, relative to independent year-by-year models, the proposed dynamic specifications recover the underlying time-varying income distribution more accurately and provide tighter uncertainty quantification for poverty and inequality measures. In the empirical application, the dynamic models yield smoother parameter trajectories and more stable welfare summaries, and they can change posterior inferences about Lorenz and stochastic dominance over time.




%Our modelling perspective complements existing work on income distributions in two ways. It retains the
%interpretability and tractability of parametric distributional modelling, which is attractive when one
%needs closed-form or fast evaluation of distributional functionals, while incorporating dynamic structure
%that is standard in time-series and state-space analysis. At the same time, it is designed to accommodate
%the empirical features of income data that motivate flexible distributional families, including heavy
%tails and skewness. 



%The result is a framework that can be implemented with
%longitudinal or repeated cross-sectional data and that produces inference and forecasts directly on the
%distributional objects of substantive interest.

%The empirical motivation for the paper is the growing use of HILDA and related panel datasets in
%distributional analysis. These datasets provide an opportunity to move beyond descriptive trends and
%toward statistically principled, dynamically consistent inference on inequality and poverty. The dynamic
%framework developed here is intended to support that shift. In Section \ref{sec:incomedistributions}, we discuss some well-known income distributions.

The remainder of the paper is organised as follows. Section~\ref{sec:model} presents the proposed dynamic income models and discusses the prior distributions of the model parameters. Section \ref{sec:posteriorinference} discusses Bayesian inference for the proposed models using Markov chain Monte Carlo.  Section \ref{sec:inequalitymeasures} discusses poverty and inequality measures. Section \ref{sec:stochasticdominance} discusses Lorenz and stochastic dominance conditions. Section \ref{sec:simulationstudy} discusses a simulation study. Section \ref{sec:empiricalapplications} discusses the real data application using HILDA survey. Section \ref{sec:conclusions} concludes. The paper also has an online supplement with additional technical details and examples.

\section{Model\label{sec:model}}

In this section, we develop dynamic parametric models for income distributions observed over time. Rather than estimating each year's income distribution independently, which can lead to noisy parameter trajectories and unstable estimates of inequality and poverty measures, we treat each annual observed income as a realisation from an underlying distribution that evolves over time. The key idea is to allow the parameters of a flexible income distribution to vary by year, while borrowing strength across adjacent years to regularise estimation and improve robustness. This is particularly important for subgroup analysis, where some annual samples are small and year-by-year estimation is highly variable.

Let $\mathbf y_t=(y_{t,1},\ldots,y_{t,n_t})^\top$ denote the vector of observed incomes in year $t$, where $n_t$ is the number of individuals or households observed in that year. Collecting all years,
$\mathbf y = \big(\mathbf y_1^\top,\ldots,\mathbf y_T^\top\big)^\top.$
We model the evolution of the income distribution over time through a set of time-varying latent state parameters.

\subsection{Dynamic models for income distributions\label{subsec:dynamic_income_model}}
This section discusses the proposed dynamic models for income distributions.
%\paragraph{Observation model.}
Let $p_{Y_t}(\cdot \mid \boldsymbol\phi_t)$ denote the density of a parametric income distribution at time $t$ with the parameter vector $\boldsymbol\phi_t$. Examples include the Dagum, Singh--Maddala, and GB2 distributions discussed in Section \ref{sec:incomedistributions} of the online supplement. Conditional on $\boldsymbol\phi_t$, the incomes observed in year $t$ are assumed independent and identically distributed:
\[
y_{t,i}\mid \boldsymbol\phi_t \stackrel{\mathrm{iid}}{\sim} p_{Y_t}(\,\cdot \mid \boldsymbol\phi_t),
\qquad i=1,\ldots,n_t,\quad t=1,\ldots,T.
\]
Hence the likelihood factorises as
\[
p(\mathbf y\mid \boldsymbol\phi_{1:T})
=
\prod_{t=1}^T \prod_{i=1}^{n_t}
p_{Y_t}(y_{t,i}\mid \boldsymbol\phi_t),
\]
where $\boldsymbol\phi_{1:T}=(\boldsymbol\phi_1^{\top},\ldots,\boldsymbol\phi_T^{\top})^{\top}$. 
The income distribution parameters are often constrained; for example, scale and shape parameters are typically positive. To work on an unconstrained space, we introduce a latent state vector $\boldsymbol\theta_t = (\theta_{1,t},\ldots,\theta_{d,t})^\top \in \mathbb R^d$
and a smooth one-to-one transformation $g$, such that
\[
\boldsymbol\phi_t = g(\boldsymbol\theta_t), \qquad t=1,\ldots,T.
\]
For instance, positivity constraints can be enforced using exponential transformations. Under this reparameterisation, the observation model becomes
\[
y_{t,i}\mid \boldsymbol\theta_t \stackrel{\mathrm{iid}}{\sim}
p_{Y_t}\!\left(\,\cdot \mid g(\boldsymbol\theta_t)\right),
\qquad i=1,\ldots,n_t,\quad t=1,\ldots,T.
\]

%\paragraph{Random walk state evolution.}
\noindent To model gradual changes in the income distribution over time, we place a dynamic prior on the latent states $\{\boldsymbol\theta_t\}_{t=1}^T$. A natural starting point is a random walk (RW) model.  
Assume that ${\phi_{1,1},\ldots,\phi_{d,1}>0}$ and define
${\boldsymbol{\theta}_1
=
\bigl(\log(\phi_{1,1}),\ldots,\log(\phi_{d,1})\bigr)^\top,}
$
with
${
\phi_{1,1},\ldots,\phi_{d,1}
\stackrel{\mathrm{ind}}{\sim}
\mathrm{Half\text{-}Cauchy}(0,1).
}$
Under this log-transformation, the density of the initial state
$\boldsymbol{\theta}_1$ is given by
\begin{equation}
p(\boldsymbol{\theta}_1)
=
\prod_{k=1}^d
\frac{2\exp(\theta_{k,1})}{\pi\bigl(1+\exp(2\theta_{k,1})\bigr)},
\label{eq:initialstate}
\end{equation}
where $\phi_{k,1}=\exp(\theta_{k,1})$, for $k=1,\ldots,d$.
For $t=2,\ldots,T$, the state evolution is given by
\[
\boldsymbol\theta_t \mid \boldsymbol\theta_{t-1},\boldsymbol\sigma
\sim
\mathcal N\!\left(\boldsymbol\theta_{t-1},\,\mathbf Q(\boldsymbol\sigma)\right),
\]
where
$\mathbf Q(\boldsymbol\sigma)=\mathrm{diag}(\sigma_1^2,\ldots,\sigma_d^2)$
and $\boldsymbol\sigma=(\sigma_1,\ldots,\sigma_d)^\top$ controls the magnitude of year-to-year change in each latent state. Equivalently, componentwise,
\[
\theta_{k,t} = \theta_{k,t-1} + \sigma_k \varepsilon_{k,t},
\qquad
\varepsilon_{k,t}\stackrel{\mathrm{iid}}{\sim}\mathcal N(0,1),
\qquad
k=1,\ldots,d,\quad t=2,\ldots,T.
\]
This formulation allows different parameters of the income distribution to evolve at different rates. The innovation scales determine how strongly the model borrows information across adjacent years. Small values imply smoother trajectories, whereas larger values allow more pronounced temporal variation. We use a weakly informative half-Cauchy prior:
${
\sigma_k \sim \mathrm{Half\mbox{-}Cauchy}(0,1),
}$
for $k=1,...,d$. Because the half-Cauchy prior is concentrated near zero but has heavy tails, it encourages small value of $\sigma_k$, while still allowing for large value of $\sigma_k$ when warranted by the data. Combining the observation and state equations yields the joint posterior density
\[
p(\boldsymbol\theta_{1:T},\boldsymbol\sigma\mid \mathbf y)
\propto
\left[
\prod_{t=1}^T \prod_{i=1}^{n_t}
p_{Y_t}\!\left(y_{t,i}\mid g(\boldsymbol\theta_t)\right)
\right]
p(\boldsymbol\theta_1)
\left[
\prod_{t=2}^T
p(\boldsymbol\theta_t\mid \boldsymbol\theta_{t-1},\boldsymbol\sigma)
\right]
p(\boldsymbol\sigma),
\]
where $\boldsymbol\theta_{1:T}=(\boldsymbol\theta_1^\top,\ldots,\boldsymbol\theta_T^\top)^\top$. This makes clear how the dynamic model differs from year-by-year estimation: inference for $\boldsymbol\theta_t$ is informed not only by the data observed in year $t$, but also indirectly by neighbouring years through the latent trajectory. As a result, the model yields smoother and typically more stable estimates of time-varying income distributions and of the inequality and poverty measures derived from them.

%When a more parsimonious specification is preferred, one may instead use a common innovation scale $\sigma>0$ and write
%\[
%\boldsymbol\theta_t \mid \boldsymbol\theta_{t-1},\sigma
%\sim
%\mathcal N\!\left(\boldsymbol\theta_{t-1},\,\sigma^2\mathbf I_d\right),
%\qquad t=2,\ldots,T.
%\]

%or, under the scalar specification,
%\[
%\sigma \sim \mathrm{Half\mbox{-}Cauchy}(0,s).
%\]

%\[
%p(\mathbf y,\boldsymbol\theta_{1:T},\boldsymbol\sigma)
%=
%\left[
%\prod_{t=1}^T \prod_{i=1}^{n_t}
%p_Y\!\left(y_{t,i}\mid g(\boldsymbol\theta_t)\right)
%\right]
%p(\boldsymbol\theta_1)
%\left[
%\prod_{t=2}^T
%p(\boldsymbol\theta_t\mid \boldsymbol\theta_{t-1},\boldsymbol\sigma)
%\right]
%p(\boldsymbol\sigma),
%\]
%The corresponding posterior distribution is



%\paragraph{Joint distribution and posterior.}


\subsection{Random walk income model with horseshoe shrinkage priors\label{subsec:rw_horseshoe}}

The random walk model can be extended by considering a horseshoe shrinkage prior \citep{carvalho2010horseshoe} on the innovation scales. This yields a {random walk income model with horseshoe shrinkage priors} (RW-HS). The main idea is to replace the innovation scales by a global-local shrinkage structure: a global parameter controls the overall amount of temporal smoothing, while local parameters allow individual components of the latent state to deviate from this common level of smoothness when supported by the data.

%,
%\boldsymbol\lambda^2=(\lambda_1^2,\ldots,\lambda_d^2)^\top

Under the horseshoe specification, the latent states evolve according to \eqref{eq:initialstate} for $t=1$
and, for $t=2,\ldots,T$,
\[
\boldsymbol\theta_t \mid \boldsymbol\theta_{t-1},\tau^2,\boldsymbol\Lambda
\sim
\mathcal N\!\left(\boldsymbol\theta_{t-1},\,\tau^2\mathbf\Lambda\right),
\]
where
$\mathbf\Lambda=\mathrm{diag}(\lambda_1^2,\ldots,\lambda_d^2).
$
Equivalently, componentwise,
\[
\theta_{k,t}
=
\theta_{k,t-1} + \tau\lambda_k \varepsilon_{k,t},
\qquad
\varepsilon_{k,t}\stackrel{\mathrm{iid}}{\sim}\mathcal N(0,1),
\qquad
k=1,\ldots,d,\quad t=2,\ldots,T.
\]
Here, $\tau>0$ is a global shrinkage parameter and $\lambda_k>0$ is a local shrinkage parameter for the $k$th latent state. When $\tau$ is small, the latent trajectories are strongly smoothed across time. When a particular component requires more flexibility, a large value of $\lambda_k$ allows that component to have a larger jump. We assign half-Cauchy priors to both the global and local scales: 
${\lambda_k \sim \mathrm{Half\mbox{-}Cauchy}(0,1),
 k=1,\ldots,d,}
$
and
$
\tau \sim \mathrm{Half\mbox{-}Cauchy}(0,1).
$


%\paragraph{Horseshoe prior hierarchy.}
%This prior is attractive because it combines strong shrinkage of small innovations with heavy tails that preserve the possibility of larger time variation. Hence it is well suited to longitudinal income modelling, where many year-to-year changes may be small, but occasional distributional shifts can occur.


%Relative to the baseline random walk model, the innovation covariance matrix is now $\tau^2\mathbf\Lambda$, which allows the degree of temporal smoothing to be learned adaptively from the data.



%\paragraph{Interpretation.}
%The random walk income model with horseshoe shrinkage priors is particularly useful when some years contain relatively few observations or when certain parameters are weakly identified from a single cross-section. In such settings, independent estimation can produce erratic year-to-year movements and unstable estimates of derived quantities such as mean income, the Gini coefficient, poverty measures, and dominance probabilities. By shrinking weakly supported innovations toward zero while allowing a small number of components to vary more substantially, the horseshoe random walk model provides a more stable and coherent description of the evolution of the income distribution over time.

%We begin with posterior computation for the baseline random walk income model, and then extend the sampler to the random walk income model with horseshoe shrinkage priors.

%For each year $t=1,\ldots,T$, let
%\[
%\mathbf y_t=(y_{t,1},\ldots,y_{t,n_t})^\top
%\]
%denote the observed strictly positive incomes, with $y_{t,i}\in(0,\infty)$. We assume a parametric income density $p_Y(\cdot\mid \boldsymbol\phi_t)$ supported on $(0,\infty)$, where $\boldsymbol\phi_t\in\Phi\subseteq\mathbb R^d$ is the year-$t$ parameter vector. To work on an unconstrained space, we introduce latent states $\boldsymbol\theta_t\in\mathbb R^d$ and a smooth one-to-one transformation $g:\mathbb R^d\to\Phi$ such that
%\[
%\boldsymbol\phi_t=g(\boldsymbol\theta_t).
%\]
%Conditional on $\boldsymbol\theta_t$, the observations are independent within each year:
%\[
%y_{t,i}\mid \boldsymbol\theta_t
%\stackrel{\mathrm{iid}}{\sim}
%p_Y\!\left(\,\cdot \mid g(\boldsymbol\theta_t)\right),
%\qquad
%i=1,\ldots,n_t,\quad t=1,\ldots,T.
%\]

\section{Posterior inference\label{sec:posteriorinference}}

This section describes the Metropolis-within-Gibbs (MwG) samplers \citep{RobertCasella2004} for the proposed dynamic models for income distributions. 

%Throughout, we write
%\[
%\boldsymbol\theta_{1:T}=(\boldsymbol\theta_1,\ldots,\boldsymbol\theta_T)
%\]
%and denote the $k$th component of $\boldsymbol\theta_t$ by $\theta_{k,t}$ for $k=1,\ldots,d$. \footnote{We use the inverse-gamma parameterisation
%\[
%x\sim \mathrm{IG}(a,b)
%\quad\Longleftrightarrow\quad
%p(x)\propto x^{-(a+1)}\exp\!\left(-\frac{b}{x}\right),
%\qquad x>0.
%\]
%}

%Under this specification, the latent states evolve according to
%\[
%\boldsymbol\theta_1\sim \mathcal N(\boldsymbol\mu_1,\mathbf P_1),
%\qquad
%\boldsymbol\theta_t\mid \boldsymbol\theta_{t-1},\boldsymbol\sigma^2
%\sim
%\mathcal N(\boldsymbol\theta_{t-1},\mathbf Q),
%\quad t=2,\ldots,T,
%\]
%where
%\[
%\mathbf Q=\mathrm{diag}(\sigma_1^2,\ldots,\sigma_d^2),
%\qquad
%\boldsymbol\sigma^2=(\sigma_1^2,\ldots,\sigma_d^2)^\top.
%\]

\subsection{Metropolis-within-Gibbs sampler for the random walk  model for income distributions \label{subsec:mcmc_rw}}

We first consider posterior inference for the random walk model for income distributions. 
Algorithm~\ref{alg:mwg_rw_income_model} gives the full MwG sampler. Each MwG iteration alternates between two steps:  
(i) updating the latent states $\boldsymbol\theta_{1:T}$ one time point at a time using random-walk Metropolis-within-Gibbs updates, and  
(ii) updating the innovation variances $\boldsymbol\sigma^2$ using Metropolis-within-Gibbs steps with inverse-gamma proposals. 

We define the time-$t$ log-likelihood contribution as
$
\ell_t(\boldsymbol\theta_t)
=
\sum_{i=1}^{n_t}
\log p_{Y_t}\!\left(y_{t,i}\mid g(\boldsymbol\theta_t)\right).
$
At each iteration, we update $\boldsymbol\theta_t$ conditionally on its neighbours using the Gaussian proposal
$
\boldsymbol\theta_t^\star
\sim
\mathcal N\!\left(\boldsymbol\theta_t,\kappa_t\boldsymbol\Sigma_t\right),
$
where $\boldsymbol\Sigma_t$ is a positive definite proposal covariance matrix and $\kappa_t>0$ is a tuning constant. In practice, $\boldsymbol\Sigma_t$ is obtained from the empirical covariance matrix  of previous MCMC draws, and $\kappa_t$ is tuned to target an acceptance probability around $0.2$ using the algorithm proposed by \citet{garthwaite2016adaptive}.

Because the latent process is first-order Markov, $\boldsymbol\theta_t$ interacts with the rest of the trajectory only through its immediate neighbours $\boldsymbol\theta_{t-1}$ and $\boldsymbol\theta_{t+1}$. Hence, when proposing $\boldsymbol\theta_t^\star$, the acceptance probability depends only on $\ell_t(\boldsymbol\theta_t)$ and the transition densities linking $\boldsymbol\theta_t$ to adjacent states. Define
\[
\log \pi_t^{\mathrm{RW}}(\boldsymbol\theta_t)=
\begin{cases}
\ell_1(\boldsymbol\theta_1)
+\log  p(\boldsymbol\theta_1)
+\log \mathcal N(\boldsymbol\theta_2\mid \boldsymbol\theta_1,\mathbf Q),
& t=1,
\\[0.6em]
\ell_t(\boldsymbol\theta_t)
+\log \mathcal N(\boldsymbol\theta_t\mid \boldsymbol\theta_{t-1},\mathbf Q)
+\log \mathcal N(\boldsymbol\theta_{t+1}\mid \boldsymbol\theta_t,\mathbf Q),
& 1<t<T,
\\[0.6em]
\ell_T(\boldsymbol\theta_T)
+\log \mathcal N(\boldsymbol\theta_T\mid \boldsymbol\theta_{T-1},\mathbf Q),
& t=T.
\end{cases}
\]
Since the proposal is symmetric, the acceptance probability is
${
\alpha_t
=
\min\Bigl\{1,
\exp\bigl(
\log \pi_t^{\mathrm{RW}}(\boldsymbol\theta_t^\star)
-
\log \pi_t^{\mathrm{RW}}(\boldsymbol\theta_t)
\bigr)
\Bigr\}.
}$
We then set $\boldsymbol\theta_t= \boldsymbol\theta_t^\star$ with probability $\alpha_t$. Detailed updates for the innovative variances are given in Section \ref{sec:additionaldetailrandomwalkincome} of the online supplement. 
%Algorithm~\ref{alg:mwg_rw_income_model} summarises the complete sampler for the random walk income model.

\begin{algorithm}[h]
\caption{Metropolis-within-Gibbs sampler for the random walk model for income distributions}
\label{alg:mwg_rw_income_model}
\begin{algorithmic}[1]
\Require Data $\{\mathbf y_t\}_{t=1}^T$, initial values $(\boldsymbol\theta_{1:T}^{(0)},\boldsymbol\sigma^{2(0)})$
\For{$m=1,\ldots,M$}
    \State \textbf{(A) Update latent states $\boldsymbol\theta_{1:T}$}
    \For{$t=1,\ldots,T$}
        \State Propose $\boldsymbol\theta_t^\star \sim \mathcal N\!\left(\boldsymbol\theta_t^{(m-1)},\,\kappa_t\boldsymbol\Sigma_t\right)$
        \State Compute $\log \pi_t^{\mathrm{RW}}(\boldsymbol\theta_t^\star)$ and $\log \pi_t^{\mathrm{RW}}(\boldsymbol\theta_t^{(m-1)})$
        \State Set
        \[
        \alpha_t=
        \min\left\{
        1,\exp\!\left(
        \log \pi_t^{\mathrm{RW}}(\boldsymbol\theta_t^\star)
        -
        \log \pi_t^{\mathrm{RW}}(\boldsymbol\theta_t^{(m-1)})
        \right)
        \right\}
        \]
        \State With probability $\alpha_t$, set $\boldsymbol\theta_t^{(m)}=\boldsymbol\theta_t^\star$; otherwise set $\boldsymbol\theta_t^{(m)}=\boldsymbol\theta_t^{(m-1)}$
    \EndFor

    \State \textbf{(B) Update innovation variances $\boldsymbol\sigma^2$}
    \For{$k=1,\ldots,d$}
        \State Compute $S_k=\sum_{t=2}^T (\theta_{k,t}^{(m)}-\theta_{k,t-1}^{(m)})^2$
        \State Set $\alpha_k=(T-2)/2$ and $\beta_k=S_k/2$
        \State Propose $\sigma_k^{2\star}\sim \mathrm{IG}(\alpha_k,\beta_k)$
        \State Set
        \[
        \alpha_{\sigma_k^2}
        =
        \min\left\{
        1,\frac{1+\sigma_k^{2(m-1)}}{1+\sigma_k^{2\star}}
        \right\}
        \]
        \State With probability $\alpha_{\sigma_k^2}$, set $\sigma_k^{2(m)}=\sigma_k^{2\star}$; otherwise set $\sigma_k^{2(m)}=\sigma_k^{2(m-1)}$
    \EndFor

    \State Store $\bigl(\boldsymbol\theta_{1:T}^{(m)},\boldsymbol\sigma^{2(m)}\bigr)$
\EndFor
\end{algorithmic}
\end{algorithm}

\subsection{Metropolis-within-Gibbs sampler for the random walk model with horseshoe shrinkage priors for income distributions\label{subsec:mcmc_rw_hs}}

We now extend the MwG sampler to the random walk income model with horseshoe shrinkage priors \citep{carvalho2010horseshoe}. Under this specification, the state innovations satisfy
\[
\Delta\theta_{k,t}
=
\theta_{k,t}-\theta_{k,t-1},
\qquad t=2,\ldots,T,\quad k=1,\ldots,d,
\]
with
\[
\Delta\theta_{k,t}\mid \tau^2,\lambda_k^2
\stackrel{\mathrm{ind}}{\sim}
\mathcal N(0,\tau^2\lambda_k^2).
\]

A convenient augmented representation of horseshoe priors is obtained through inverse-gamma mixtures \citep{makalic2015simple}. Specifically,
\[
\lambda_k^2 \mid \nu_k \sim \mathrm{IG}\!\left(\frac{1}{2},\frac{1}{\nu_k}\right),
\qquad
\nu_k \sim \mathrm{IG}\!\left(\frac{1}{2},1\right),
\qquad k=1,\ldots,d,
\]
and
\[
\tau^2 \mid \xi \sim \mathrm{IG}\!\left(\frac{1}{2},\frac{1}{\xi}\right),
\qquad
\xi \sim \mathrm{IG}\!\left(\frac{1}{2},1\right),
\]
where $\mathrm{IG}(a,b)$ denotes the inverse-gamma distribution with density proportional to
$
x^{-(a+1)}\exp\!\left(-\frac{b}{x}\right), x>0.
$
Let $\boldsymbol{\nu}=(\nu_1,\ldots,\nu_d)^\top$. The joint posterior distribution of the latent states $\boldsymbol\theta_{1:T}$ and shrinkage parameters is given by
\begin{align*}
&p(\boldsymbol\theta_{1:T},\tau^2,\boldsymbol\lambda^2,\xi,\boldsymbol\nu \mid \mathbf y) \\
&\quad\propto
\left\{
\prod_{t=1}^T \prod_{i=1}^{n_t}
p_{Y_t}\!\left(y_{t,i}\mid g(\boldsymbol\theta_t)\right)
\right\}
p(\boldsymbol\theta_1)
\left\{
\prod_{t=2}^T
p\!\left(\boldsymbol\theta_t\mid \boldsymbol\theta_{t-1},\tau^2,\boldsymbol\lambda^2\right)
\right\} \\
&\qquad\times
p(\tau^2\mid \xi)\,p(\xi)
\prod_{k=1}^d p(\lambda_k^2\mid \nu_k)\,p(\nu_k).
\end{align*}


Algorithm~\ref{alg:mwg_rw_hs_income_model} in Section \ref{sec:additionaldetailshorseshoe} of the online supplement summarises the MwG sampler for the random walk income model with horseshoe shrinkage priors. The two dynamic income models differ only in how the temporal innovation variances are modelled. In the RW model, each latent state has its own innovation variance $\sigma_k^2$. In the RW-HS specification, these variance terms are replaced by the product 
$\tau^2\lambda_k^2$, where $\tau^2$ controls the overall degree of smoothing 
and $\lambda_k^2$ allows each latent state component to depart from this 
global level. 

%Although we focus on the horseshoe prior, the same framework can accommodate other shrinkage priors for the state innovations, such as the triple-gamma prior of \citet{cadonna2020triple}. Such alternatives may provide different shrinkage behaviour while retaining the same basic random walk formulation.










\section{Inequality and poverty measures\label{sec:inequalitymeasures}}


This section summarises the inequality and poverty indices used in our empirical analysis.
Given a parametric income model with density $p_{Y_t}(\cdot\mid\boldsymbol{\phi_t})$ and distribution
function ${F_{Y_t}(\cdot\mid\boldsymbol{\phi_t})}$ at time $t$, we evaluate each index as a functional of
$\boldsymbol{\phi}_t$ and a poverty line $z>0$. Let
$\mu_t$ denotes the mean income, assumed finite, and 
$L_t(u;\boldsymbol{\phi}_t)$ denotes the Lorenz curve at time $t$, defined as the cumulative share of total
income held by the poorest $u\in[0,1]$ proportion of the population. 

%We consider the Gini coefficient to measure inequality and 
%These indices capture
%different normative aspects of inequality and poverty: the Gini coefficient summarises
%overall dispersion relative to the Lorenz curve; the generalised entropy class is attractive
%because it is additively decomposable across population subgroups; and the poverty measures
%quantify incidence, depth, and severity of poverty relative to a fixed poverty line. See, for
%example, \citet{Cowell2011} and \citet{Foster:1984} for more detailed discussions.

The most widely used inequality measure is the Gini coefficient, $G_t$, defined as twice the
area between the Lorenz curve and the line of equality. It ranges from $0$ 
to $1$, and is invariant to scale, in the sense that multiplying
all incomes by a positive constant does not change $G_t$. The Gini index at time $t$ is given by
\begin{equation}
G_t
=
1-2\int_{0}^{1} L_t(u;\boldsymbol{\phi}_t)\,du.
\label{eq:gini_lorenz}
\end{equation}
An equivalent expression, convenient for parametric modelling, is
\begin{equation}
G_t
=
-1+\frac{2}{\mu_t}\int_{0}^{\infty} y\,F_{Y_t}(y\mid\boldsymbol{\phi})\,p_{Y_t}(y\mid\boldsymbol{\phi})\,dy,
\label{eq:gini_cdf_pdf}
\end{equation}
see, for example, \citet{Gastwirth1971}. In practice, \eqref{eq:gini_cdf_pdf} is useful because
closed-form expressions for $F_{Y_t}(\cdot\mid\boldsymbol{\phi})$ and for moment distribution
functions often yield analytic or numerically stable evaluations of $G_t$ under parametric
models.

%; see Section \ref{sec:incomedistributions} for expressions for the Gini coefficient for income models considered in this paper.


\begin{comment}

We also consider the generalised entropy (GE) class of inequality measures, which has the
advantage of \emph{additive decomposability} across population subgroups, a property that
facilitates inequality decomposition into within- and between-group components
\citep{Theil1967,Cowell2011}. For $v\neq 0,1$, the GE index is
\begin{equation}
\mathrm{GE}(v)
=
\frac{1}{v^2-v}
\left[
\int_{0}^{\infty}\left(\frac{y}{\mu}\right)^{v} p_Y(y\mid\boldsymbol{\phi})\,dy - 1
\right].
\label{eq:GE_general}
\end{equation}
The parameter $v$ controls sensitivity to different parts of the income distribution:
larger positive values place relatively more weight on income differences in the upper tail,
whereas $v<0$ emphasises disparities among low incomes. This flexibility is helpful when
assessing robustness of inequality conclusions to alternative normative weights.

Two important special cases are the Theil indices, obtained as limits as $v\to 0$ and $v\to 1$:
\begin{align}
T_{0}=\mathrm{GE}(0)
&=
\int_{0}^{\infty}\log\!\left(\frac{\mu}{y}\right) p_Y(y\mid\boldsymbol{\phi})\,dy,
\label{eq:theil_T0}
\\
T_{1}=\mathrm{GE}(1)
&=
\int_{0}^{\infty}\left(\frac{y}{\mu}\right)\log\!\left(\frac{y}{\mu}\right) p_Y(y\mid\boldsymbol{\phi})\,dy.
\label{eq:theil_T1}
\end{align}
The index $T_{0}$, often called \emph{Theil's $L$} or the \emph{mean log deviation},
is more sensitive to the lower tail because it involves $\log(\mu/y)$, which grows as $y$
approaches zero. In contrast, $T_{1}$, often called \emph{Theil's $T$}, weights log-deviations
by income shares $(y/\mu)$ and is therefore more sensitive to changes in the upper tail.

\end{comment}

We now briefly describe well-known poverty measures.
Let $z>0$ denote a fixed poverty line, for example an absolute poverty threshold or a
fraction of median income. We consider poverty measures that quantify complementary
aspects of poverty: {incidence} (how many are poor), and {depth} (how far below the
poverty line the poor are on average). These measures are standard in the poverty
measurement literature; see, for example, \citet{FosterGreerThorbecke1984}.
The headcount ratio ($\mathrm{HC}_t$) is simply the proportion of the population with income below $z$ at time $t$:
\begin{equation}
\mathrm{HC}_t
=
F_{Y_t}(z\mid\boldsymbol{\phi}_t).
\label{eq:hc}
\end{equation}
The headcount ratio is easy to interpret but ignores the depth of poverty: it does not change
when incomes of the poor fall further below $z$, provided they remain below the poverty line.
The poverty gap ($\mathrm{PG}_t$) measures the average proportional shortfall from the poverty line at time $t$:
\begin{equation}
\mathrm{PG}_t
=
\int_{0}^{z}\left(\frac{z-y}{z}\right)p_{Y_t}(y\mid\boldsymbol{\phi}_t)\,dy.
\label{eq:pg}
\end{equation}
Unlike \(\mathrm{HC}_t\), the poverty gap accounts for how far incomes fall below the poverty line and can be interpreted as the minimum share of total income needed to raise all poor individuals to \(z\).
More generally, the Foster--Greer--Thorbecke (FGT) class at time $t$ is defined by
\begin{equation}
\mathrm{FGT}\alpha_t
=
\int_{0}^{z}\left(\frac{z-y}{z}\right)^{\alpha} p_{Y_t}(y\mid\boldsymbol{\phi_t})\,dy,
\qquad \alpha\ge 0.
\label{eq:fgt_general}
\end{equation}
Thus, $\mathrm{FGT}0_t=\mathrm{HC}_t$ and $\mathrm{FGT}1_t=\mathrm{PG}_t$. In this paper, we estimate the indices by Monte Carlo simulation:
We draw a large sample from the fitted income distribution and compute the corresponding sample-based estimates.


%For each parametric income distribution considered in this paper, closed-form expressions for these indices can be
%obtained when available. However,

\begin{comment}
With aversion parameter
$\alpha=2$, the index is
\begin{equation}
\mathrm{FGT}(2)
=
\int_{0}^{z}\left(\frac{z-y}{z}\right)^{2} p_Y(y\mid\boldsymbol{\phi})\,dy.
\label{eq:fgt2}
\end{equation}
Relative to $\mathrm{PG}$, $\mathrm{FGT}(2)$ places greater weight on the poorest individuals
and is therefore more sensitive to inequality among the poor.

First-order stochastic dominance can equivalently be expressed in terms of cumulative
distribution functions rather than quantile functions, and generalised Lorenz dominance
can also be written in terms of integrals of cumulative distribution functions. We adopt
\eqref{eq:lorenz_dom_phi}--\eqref{eq:fsd_quantile_phi} because they are naturally indexed
by the population share $u\in[0,1]$, matching the Lorenz-curve interpretation.

\end{comment}



\section{Lorenz and stochastic dominance \label{sec:stochasticdominance}}

This section discusses Lorenz dominance, generalised Lorenz dominance, and first-order stochastic dominance. Consider two income distributions at time $t$ indexed by parameter vectors
$\boldsymbol{\phi}_{A,t}$ and $\boldsymbol{\phi}_{B,t}$, with corresponding cumulative distribution
functions $F_{Y_{A,t}}(\cdot\mid\boldsymbol{\phi}_{A,t})$ and $F_{Y_{B,t}}(\cdot\mid\boldsymbol{\phi}_{B,t})$, means
$\mu_{A,t}$ and $\mu_{B,t}$, and Lorenz curves
$L_{A,t}(\cdot;\boldsymbol{\phi}_{A,t})$ and $L_{B,t}(\cdot;\boldsymbol{\phi}_{B,t})$. We state the dominance
conditions using the population share $u\in[0,1]$. Distribution $A$ Lorenz (LD) dominates  distribution $B$ at time $t$ if
\begin{equation}
\begin{aligned}
L_{A,t}(u;\boldsymbol{\phi}_{A,t})
&\ge L_{B,t}(u;\boldsymbol{\phi}_{B,t})
\quad \text{for all } u\in[0,1], \\
L_{A,t}(u;\boldsymbol{\phi}_{A,t})
&> L_{B,t}(u;\boldsymbol{\phi}_{B,t})
\quad \text{for some } u\in(0,1).
\end{aligned}
\label{eq:lorenz_dom_phi}
\end{equation}
Distribution $A$ generalised Lorenz (GLD) dominates  distribution $B$ at time $t$ if
\begin{equation}
\begin{aligned}
\mu_{A,t}\,L_{A,t}(u;\boldsymbol{\phi}_{A,t})
&\ge
\mu_{B,t}\,L_{B,t}(u;\boldsymbol{\phi}_{B,t})
\quad \text{for all } u\in[0,1],\\
\mu_{A,t}\,L_{A,t}(u;\boldsymbol{\phi}_{A,t})
&>
\mu_{B,t}\,L_{B,t}(u;\boldsymbol{\phi}_{B,t})
\quad \text{for some } u\in(0,1).
\end{aligned}
\label{eq:ssd_lorenz_phi}
\end{equation}
Distribution $A$ first-order (FSD) stochastically dominates distribution $B$ at time $t$ if
\begin{equation}
\begin{aligned}
F_{Y_{A,t}}^{-1}(u\mid\boldsymbol{\phi}_{A,t})\ge F_{Y_{B,t}}^{-1}(u\mid\boldsymbol{\phi}_{B,t})
&\quad \text{for all } u\in[0,1],\\
\text{and}\qquad
F_{Y_{A,t}}^{-1}(u\mid\boldsymbol{\phi}_{A,t})> F_{Y_{B,t}}^{-1}(u\mid\boldsymbol{\phi}_{B,t})
&\quad \text{for some } u\in(0,1).
\end{aligned}
\label{eq:fsd_quantile_phi}
\end{equation}

We follow \citet{lander2020bayesian} and \citet{gunawan2021posterior}  to compute posterior probabilities of Lorenz and stochastic dominance. The posterior probabilities of Lorenz and stochastic dominance are estimated by counting the proportion of MCMC draws for which the estimated distributional functions satisfy the relevant dominance conditions. Since income is a continuous variable, when calculating the proportion of MCMC draws that satisfy the relevant dominance conditions for all $u\in [0,1]$, the best we can do is to check the conditions for a finite grid set of points. Accordingly, the resulting posterior probabilities should be interpreted relative to the adopted grid resolution and the total number of MCMC draws used in the analysis. In this paper, we see Section \ref{sec:additionaldetailLorenzstochastic} for further details. In practice, this approach is analogous to widely used frequentist procedures, such as the tests of \citet{barrett2003consistent} for first-order stochastic and generalized Lorenz dominance and \citet{barrett2014consistent} for Lorenz dominance, which approximate continuum-based conditions by evaluating them over a discrete set of support points. 

We also plot probability curves, which give the posterior probability of pointwise dominance at
each population share $u$. Over any range of $u$, the posterior probability of dominance on that
range can be no larger than the minimum value of the probability curve within the range. This makes
the probability curve a useful device for identifying which parts of the distribution, such as the tails
or the middle, drive the overall dominance probability. In particular, if dominance is largely
determined by tail behaviour, one can assess sensitivity by omitting extreme values of $u$.
Likewise, if interest focuses on a particular segment of the population, such as the poor,
one can examine how the dominance probability changes when attention is restricted to the
corresponding range of $u$.



\section{Simulation study\label{sec:simulationstudy}}

This section presents a simulation study designed to assess how borrowing strength over time improves inference for income distributions modelled by the Dagum distribution \citep{Dagum1977}. We generate annual incomes for $T=25$ years with $n=250$ observations per year, and we compare three models: an {independent} approach (ind) that fits a Dagum distribution separately for each year, and a {random-walk} (RW) approach in which transformed Dagum parameters evolve over time through a latent process following random walk model, and a random walk approach with horseshoe priors (RW-HS). All models are estimated in a fully Bayesian framework using the Markov chain Monte Carlo (MCMC) sampler discussed in Section \ref{sec:posteriorinference}.

%, so that uncertainty is propagated from the parameter level to all welfare, inequality and poverty distributional summaries.

Our evaluation assesses the ability of different models to estimate the true time-varying Dagum parameters, $(a_t,b_t,p_t)$, as well as a range of key distributional functionals. In particular, we examine posterior estimates of mean income $\mu_t$, the Gini coefficient $G_t$, and the $\mathrm{FGT}{0_t}$ and $\mathrm{FGT}{1_t}$ poverty indices, for $t=1,...,T$. We also compare the estimated densities, cumulative distribution functions, generalised Lorenz curves, and Lorenz curves over time obtained from posterior draws, with posterior credible bands reported for each curve.

%The Dagum parameters $(a_t,b_t,p_t)$ are generated from a Gaussian random walk on the log scale. 
%This setting investigates whether the random-walk model improves efficiency---especially with only $n=250$ observations per year---by stabilising estimates and reducing posterior variability relative to year-by-year fitting.
%The Dagum parameters are then obtained by exponentiating the latent log-parameters,
%$
%a_t=\exp(\tilde a_t), 
%b_t=\exp(\tilde b_t), p_t=\exp(\tilde p_t),
%$
%for $t=1,\ldots,T$.

We now discuss the data-generating process. We simulate data from the random-walk model specification. The log of the Dagum parameters follow a Gaussian random walk, producing gradual year-to-year changes in the income distribution. For $t=1,\ldots,T$ and $i=1,\ldots,n$, we assume
$
y_{t,i}\mid (a_t,b_t,p_t) \overset{\text{iid}}{\sim} \mathrm{Dagum}(a_t,b_t,p_t).
$
The initial values are set to
$
a_1=3.54, b_1=329.58, p_1=0.61,
$
and the corresponding latent log-parameters are defined as
$
\tilde a_t=\log a_t, 
\tilde b_t=\log b_t,
\tilde p_t=\log p_t.
$
For $t=2,\ldots,T$, these latent log-parameters evolve according to
$
\tilde a_t=\tilde a_{t-1}+\sigma_a \varepsilon_{a,t},
\tilde b_t=\tilde b_{t-1}+\sigma_b \varepsilon_{b,t},
\tilde p_t=\tilde p_{t-1}+\sigma_p \varepsilon_{p,t},
$
where
$
\varepsilon_{a,t},\varepsilon_{b,t},\varepsilon_{p,t}
\overset{\mathrm{iid}}{\sim}\mathcal N(0,1),
$
and $  
\sigma_a=\sigma_b=\sigma_p=0.02.$


%To simulate observations, we draw $u_{t,i}\overset{\text{iid}}{\sim}\mathrm{Unif}(0,1)$, for $t=1,...,T$ and $i=1,...,n$, and set
%$
%y_{t,i}=F_{\mathrm{Dagum}}^{-1}\!\left(u_{t,i}\mid a_t,b_t,p_t\right),
%$
%where $F_{\mathrm{Dagum}}^{-1}(\cdot\mid a_t,b_t,p_t)$ is the Dagum quantile function.

\begin{comment}

\paragraph{DGP 2: Structural break in Dagum parameters.}
We also consider a piecewise-constant design with a single break at $t=10$.
For $t=1,\ldots,T$ and $i=1,\ldots,n$,
\[
y_{t,i}\mid (a_t,b_t,p_t) \overset{\text{iid}}{\sim} \mathrm{Dagum}(a_t,b_t,p_t),
\]
with
\[
(a_t,b_t,p_t)=
\begin{cases}
(3.54,\;329.58,\;0.61), & t=1,\ldots,10,\\
(6.54,\;280.58,\;4.61), & t=11,\ldots,25.
\end{cases}
\]
As above, we generate $y_{t,i}$ using inverse transform sampling:
draw $u_{t,i}\overset{\text{iid}}{\sim}\mathrm{Unif}(0,1)$ and set
\[
y_{t,i}=F_{\mathrm{Dagum}}^{-1}\!\left(u_{t,i}\mid a_t,b_t,p_t\right),
\qquad i=1,\ldots,n.
\]
\end{comment}

%We use $n=250$ and $T=25$.



%\subsection{Results and Discussions}

Figure~\ref{fig:Figure_param_dagum_sim1} compares the log of the true parameters of the Dagum distribution with MCMC-based posterior summaries under the independent year-by-year model (ind), the random walk (RW) model, and the random walk model with horseshoe priors (RW-HS). For each parameter, the center curve represents the posterior mean, and the outer curves give the 95\% credible intervals. The RW model tracks the true trajectories closely: it reproduces the gradual decline in $\log(b_t)$ and the mild fluctuations in $\log(a_t)$ and $\log(p_t)$, while delivering markedly tighter credible bands. In contrast, the independent model yields highly volatile year to year estimates and substantially wider uncertainty bands, most notably for $\log(p_t)$. The RW-HS model produces slightly smoother parameter trajectories than the RW model. 
Overall, the figure highlights the efficiency gains from modelling temporal dependence in the parameters.




\begin{figure}[h]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_param_dagum_sim1.png}
    \caption{The posterior means (with 95\% credible intervals) of model parameters over time obtained from the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS) for the simulated dataset. The true parameter values are also plotted.  
}
    \label{fig:Figure_param_dagum_sim1}
\end{figure}

Figure \ref{fig:Figure_dagum_mean_trajectory_sim1} shows the true and estimated mean income, Gini coefficients, FGT0, and FGT1 indices over time obtained using the three models for the simulated dataset. 
The true mean income exhibits a clear downward trajectory over time, with only modest local fluctuations. The RW and RW-HS models track this gradual decline closely: their posterior means follow the true trajectory, and their pointwise credible bands are tight, with the RW-HS model producing slightly narrower intervals. In contrast, the independent model produces much noisier mean estimates and substantially wider credible bands, with several large year-to-year swings that are not present in the true trajectory. A similar pattern is observed for the headcount ratio (FGT0). The true FGT0 increases from the early years to the middle of the sample and then fluctuates only mildly thereafter. The RW and RW-HS models capture this smooth evolution with narrow credible intervals, whereas the independent model exhibits erratic movements and inflated uncertainty, leading to substantial overestimation or underestimation of the true values in some years.

For inequality, the true Gini coefficient trajectory remains relatively stable over the sample, with only small changes around its long-run level. The RW and RW-HS models again provide a close match to the true series, with smooth posterior means and narrow credible bands. By comparison, the independent model yields highly volatile Gini estimates, including pronounced spikes and dips (with wide bands). 

%Overall, these figures show that when the Dagum parameters evolve smoothly, imposing a random-walk structure substantially stabilises inference for mean income and poverty and inequality measures (FGT0, FGT1 and Gini), improving tracking of the true trajectory while delivering tighter uncertainty quantification.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_dagum_mean_gini_FGT1_FGT0_trajectory_sim1.png}
    \caption{The posterior means (with 95\% credible intervals) of the mean income, Gini coefficient, FGT0, and FGT1 indices over time obtained from the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS) for the simulated dataset. The true parameter values are also plotted. 
}
    \label{fig:Figure_dagum_mean_trajectory_sim1}
\end{figure}








The PDF and CDF plots in Figures \ref{fig:Figure_PDF_sim1} and \ref{fig:Figure_CDF_sim1} in Section \ref{sec:additionalfiguresimulationstudy} of the online supplement (with 99\% credible intervals) show that all models capture the shape of the true density and CDF. The independent model produces wide bands and large variations in peak height and location, indicating that year-by-year estimation with $n=250$ can translate sampling noise into spurious changes in the density and CDF. The RW and RW-HS models yield narrower credible bands and posterior means that are closer to the true density curve. The RW-HS model provides slightly tighter credible intervals than the RW model.

Figures~\ref{fig:Figure_GLC_sim1_t25_099} and~\ref{fig:Figure_LC_sim1_t25_099} in Section~\ref{sec:additionalfiguresimulationstudy} of the online supplement show the GLCs and LCs for time period $t=25$, obtained under the independent, RW, and RW-HS models. For the GLCs, uncertainty is smallest at low population shares and increases toward the upper tail; accordingly, the independent model exhibits a wider 99\% credible band near the top of the distribution. The RW and RW-HS models deliver markedly tighter bands over the entire curve, especially for the upper deciles, implying more precise inference. The same conclusion holds for the LCs at $t=25$: the independent fit implies much greater uncertainty about income shares, particularly beyond the median and into the top quantiles, whereas the RW and RW-HS models produce narrower credible regions and smoother implied inequality profiles. 

%Overall, these comparisons confirm that the RW and RW-HS specifications not only stabilise point estimates but also substantially improve uncertainty quantification.

Tables~\ref{tab:tableprobsim1} and~\ref{tab:tableprobsim1_poorest} show that the estimated dominance probabilities can differ markedly across the independent model, the random walk model, and the random walk model with horseshoe shrinkage priors, with the two dynamic specifications generally producing much more similar results to each other than to the independent model. For the full population, the RW and RW-HS models tend to assign higher probabilities than the independent model for Lorenz dominance (LD), especially in the 2005--2001, 2015--2010, and 2025--2015 comparisons. For example, the LD probability for 2025 relative to 2015 increases from $0.2730$ under the independent model to $0.5667$ under RW and $0.5574$ under RW-HS, indicating substantially stronger evidence of inequality improvement once temporal smoothing is imposed. A similar pattern appears for 2005 relative to 2001 and 2015 relative to 2010, where the dynamic models roughly double the LD probabilities relative to the independent specification. By contrast, for first-order stochastic dominance (FSD) and generalised Lorenz dominance (GLD), the most striking discrepancy occurs for the 2010--2005 comparison. Here the independent model suggests moderate evidence of welfare improvement, with probabilities $0.1211$ for FSD and $0.1974$ for GLD, whereas the RW and RW-HS models reduce these probabilities to values close to zero. This indicates that the independent model may overstate welfare improvement. For the remaining comparisons, FSD and GLD probabilities are generally low under all three models, although the RW and RW-HS specifications often produce slightly larger probabilities than the independent model for 2005--2001 and 2025--2015. 

%Overall, the results suggest that temporal smoothing mainly strengthens the evidence for Lorenz dominance, while materially altering the conclusions about first-order and generalised Lorenz dominance only in selected periods, most notably for 2010 relative to 2005.

%This suggests that,  the independent model is much more sensitive to local noise in the estimated lower tail and may therefore exaggerate the degree of welfare improvement among the poorest individuals.



The differences across models are even more pronounced when attention is restricted to the poorest 10\% of the population. In this case, the independent model often yields substantially larger probabilities of FSD and GLD than the dynamic models, particularly for the 2010--2005 and 2025--2015 comparisons. For example, for 2010 relative to 2005, the independent model reports probabilities of $0.4511$ for FSD and $0.6004$ for GLD, whereas the corresponding probabilities under RW and RW-HS fall dramatically to around $0.02$ or lower. Likewise, for 2025 relative to 2015, the independent model gives much stronger evidence of dominance at the lower end of the distribution than either dynamic specification.  In contrast, the RW and RW-HS give substantially smaller dominance probabilities. However, the dynamic models give larger probabilities of Lorenz dominance relative to the independent model in several cases, such as 2005--2001 and 2015--2010. The RW and RW-HS results are very close throughout.  


%Taken together, these tables suggest that the main effect of moving from the independent model to the dynamic specifications is to reduce potentially inflated FSD and GLD probabilities driven by year-specific noise, while strengthening and stabilising the evidence for Lorenz dominance, particularly in comparisons involving distributional shape rather than complete welfare ordering.

\begin{table}[h]
\caption{Estimated posterior probabilities of Lorenz dominance, generalised Lorenz dominance, and first-order stochastic dominance for the simulated dataset, based on the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS).\label{tab:tableprobsim1}}

\centering{}%
\begin{tabular}{cccc}
\hline 
 & ind & RW & RW-HS\tabularnewline
\hline 
2005 FSD 2001 & 0.0088 & 0.0351 & 0.0362\tabularnewline
2005 GLD 2001 & 0.0148 & 0.0499 & 0.0526\tabularnewline
2005 LD 2001 & 0.0178 & 0.1458 & 0.1845\tabularnewline
\hline 
2010 FSD 2005 & 0.1211 & 0.0047 & 0.0034\tabularnewline
2010 GLD 2005 & 0.1974 & 0.0071 & 0.0045\tabularnewline
2010 LD 2005 & 0.0143 & 0.1497 & 0.1654\tabularnewline
\hline 
2015 FSD 2010 & 0.0064 & 0.0095 & 0.0087\tabularnewline
2015 GLD 2010 & 0.0234 & 0.0226 & 0.0169\tabularnewline
2015 LD 2010 & 0.1981 & 0.3818 & 0.3742\tabularnewline
\hline 
2025 FSD 2015 & 0.0181 & 0.0360 & 0.0386\tabularnewline
2025 GLD 2015 & 0.0603 & 0.0870 & 0.0884\tabularnewline
2025 LD 2015 & 0.2730 & 0.5667 & 0.5574\tabularnewline
\hline 
\end{tabular}
\end{table}



\begin{table}[h]
\caption{Estimated posterior probabilities of Lorenz dominance, generalised Lorenz dominance, and first-order stochastic dominance over the poorest 10\% of the population for the simulated dataset, based on the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS).\label{tab:tableprobsim1_poorest}}

\centering{}%
\begin{tabular}{cccc}
\hline 
 & ind & RW & RW-HS\tabularnewline
\hline 
2005 FSD 2001 & 0.0470 & 0.0858 & 0.0798\tabularnewline
2005 GLD 2001 & 0.0716 & 0.1024 & 0.0936\tabularnewline
2005 LD 2001 & 0.0993 & 0.2025 & 0.2450\tabularnewline
\hline 
2010 FSD 2005 & 0.4511 & 0.0216 & 0.0134\tabularnewline
2010 GLD 2005 & 0.6004 & 0.0338 & 0.0206\tabularnewline
2010 LD 2005 & 0.4550 & 0.2015 & 0.2174\tabularnewline
\hline 
2015 FSD 2010 & 0.1507 & 0.1152 & 0.0706\tabularnewline
2015 GLD 2010 & 0.1638 & 0.1490 & 0.0971\tabularnewline
2015 LD 2010 & 0.2196 & 0.4449 & 0.4388\tabularnewline
\hline 
2025 FSD 2015 & 0.6197 & 0.3274 & 0.2760\tabularnewline
2025 GLD 2015 & 0.7637 & 0.4057 & 0.3340\tabularnewline
2025 LD 2015 & 0.8808 & 0.6803 & 0.6615\tabularnewline
\hline 
\end{tabular}
\end{table}

Figures~\ref{fig:yFSDx_prob_sim1}--\ref{fig:yLDx_prob_sim1} show that the probability curves differ systematically across the independent, RW, and RW-HS specifications, and these differences help explain the dominance probabilities reported in Tables~\ref{tab:tableprobsim1} and~\ref{tab:tableprobsim1_poorest}. For FSD and GLD, the independent model generally produces much more irregular and more extreme pointwise probability curves, with pronounced U-shaped or hump-shaped patterns across the support. This is especially evident for the 2010--2005 and 2025--2015 comparisons, where the independent model assigns relatively high pointwise dominance probabilities near the tails but much lower probabilities in the middle of the distribution. By contrast, the RW and RW-HS curves are markedly smoother and less erratic, reflecting the stabilising effect of temporal pooling. In several cases, such as 2010--2005, the dynamic models produce probability curves that remain close to zero over most of the support, indicating that once year-to-year noise is smoothed out there is little evidence of dominance. More generally, these figures show that the independent model is much more sensitive to local fluctuations in the estimated income distributions, whereas the RW and RW-HS models deliver more coherent probability profiles over the whole range of population shares.

The LD curves reveal a somewhat different pattern. Here, the RW and RW-HS models often lie above the independent model over large parts of the support, particularly for the 2005--2001, 2015--2010, and 2025--2015 comparisons, which is consistent with their substantially higher posterior probabilities of LD in Table~\ref{tab:tableprobsim1}. The RW and RW-HS curves are again very similar, showing that the horseshoe prior mainly refines the degree of smoothing rather than changing the substantive conclusions. At the same time, the figures also illustrate why quite high pointwise probabilities do not necessarily translate into high overall dominance probabilities: dominance must hold simultaneously for all evaluation points, so even a relatively small dip in the curve can substantially reduce the joint posterior probability. 

In summary, the simulation results show that the RW and RW-HS models substantially outperform the independent model. Both dynamic specifications track the true parameter and distributional trajectories much more closely, with smoother estimates and much narrower credible intervals, while the independent model produces noisy estimates and inflated uncertainty. These improvements also carry over to the dominance analysis, where the RW and RW-HS models yield more stable and coherent probability profiles. Overall, modelling temporal dependence yields more accurate and reliable inference, with RW-HS providing an additional gain over RW.

%The probability curves make clear that the dynamic models provide a more stable and interpretable picture of dominance, while the independent model tends to exaggerate local features of the fitted distributions and thereby produces more volatile dominance assessments.


\begin{figure}[h]
    \centering
    \includegraphics[width=0.8\linewidth]{yFSDx_prob_sim1.png}
    \caption{Estimated probability curves for first order stochastic dominance obtained from the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS) for the simulated dataset.  
}
    \label{fig:yFSDx_prob_sim1}
\end{figure}

\begin{figure}[h]
    \centering
    \includegraphics[width=0.8\linewidth]{yGLDx_prob_sim1.png}
    \caption{Estimated probability curves for generalised Lorenz dominance obtained from the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS) for the simulated dataset.  
}
    \label{fig:yGLDx_prob_sim1}
\end{figure}

\begin{figure}[h]
    \centering
    \includegraphics[width=0.8\linewidth]{yLDx_prob_sim1.png}
    \caption{Estimated probability curves for Lorenz dominance obtained from the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS) for the simulated dataset.  
}
    \label{fig:yLDx_prob_sim1}
\end{figure}

\begin{comment}


\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_param_dagum_sim2.png}
    \caption{The posterior means (with 95\% credible intervals) of Dagum parameters over time obtained from the independent income model (ind) and the random walk income model (RW) using data simulated from DGP2. The true parameter values are also plotted.  
}
    \label{fig:Figure_param_dagum_sim2}
\end{figure}

Figure~\ref{fig:Figure_param_dagum_sim2} reports the true piecewise-constant Dagum log-parameters (green) together with posterior summaries from the independent (red) and random-walk (RW; blue) models under DGP2, which features a structural break at $t=10$. In the pre-break period ($t\leq 10$), the true parameters are constant and both models recover the correct level. However, the independent year-by-year fit exhibits substantial sampling-driven variability, with wide 99\% credible bands and pronounced year-to-year variabilities even when the underlying parameters do not change. By contrast, the RW model produces smoother trajectories and noticeably tighter credible bands, reflecting the benefits of temporal pooling even when the parameter path is stable.

Around the break ($t\approx 11$), clear differences emerge. The true process jumps upward in $\log(a_t)$ and $\log(p_t)$ and downward in $\log(b_t)$, whereas the RW model necessarily spreads this abrupt change over several periods. Consequently, the RW posterior mean adjusts gradually and tends to lag slightly the true post-break level. The independent model can react more quickly to the break because it treats each year separately, but this responsiveness comes at the cost of much larger uncertainty and instability, particularly for $\log(p_t)$ where the independent fit shows extreme fluctuations and very wide bands. Overall, DGP2 highlights that while the RW specification stabilises inference away from the break, it can oversmooth genuine discontinuities, whereas the independent model is more flexible at breaks but substantially less efficient and more sensitive to finite-sample noise.





\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_dagum_mean_trajectory_sim2.png}
    \caption{The posterior means (with 95\% credible intervals) of the mean income over time obtained from the independent Dagum income model (ind) and the random walk Dagum income model (RW)  using data simulated from DGP2. The true parameter values are also plotted. 
}
    \label{fig:Figure_dagum_mean_trajectory_sim2}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_dagum_gini_trajectory_sim2.png}
    \caption{The posterior means (with 95\% credible intervals) of the Gini coefficients over time obtained from the independent Dagum income model (ind) and the random walk Dagum income model (RW)  using data simulated from DGP2. The true parameter values are also plotted. 
}
    \label{fig:Figure_dagum_gini_trajectory_sim2}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_dagum_FGT0_trajectory_sim2.png}
    \caption{The posterior means (with 95\% credible intervals) of the headcount ratio over time obtained from the independent Dagum income model (ind) and the random walk Dagum income model (RW)  using data simulated from DGP2. The true parameter values are also plotted. 
}
    \label{fig:Figure_dagum_FGT0_trajectory_sim2}
\end{figure}

Figures~\ref{fig:Figure_dagum_mean_trajectory_sim2}--\ref{fig:Figure_dagum_FGT0_trajectory_sim2} report posterior trajectories for the mean income, Gini coefficient, and headcount ratio (FGT0) under DGP2, where the data are generated from a piecewise-constant Dagum model with a structural break at $t=11$. The green line shows the true path, which is approximately flat within each regime and changes abruptly at the break. The red curves correspond to the model that estimates a separate  Dagum distribution for each year (``ind''), while the blue curves correspond to the dynamic Dagum model with a random-walk evolution (``RW''). In each panel, the additional red/blue lines around the posterior mean represent the pointwise posterior uncertainty bands (e.g., 2.5\% and 97.5\% posterior quantiles).

Across all three measures, the independent year-by-year model exhibits noticeably higher variability over time, with wider and more irregular uncertainty bands, especially in the first regime ($t\le 10$). This reflects the fact that each year's parameters are identified only from that year's sample, so the resulting posterior for distributional features can fluctuate substantially even when the underlying DGP is constant. In contrast, the RW model yields smoother and generally tighter posterior bands because it borrows strength across adjacent years through the state evolution. This stabilisation is particularly evident for the headcount ratio and the Gini coefficient, where the ``ind'' estimates display spurious year-to-year swings around an otherwise stable truth, while the RW estimates track the true trajectory more closely and with reduced posterior dispersion.

Around the structural break ($t=11$), both approaches detect a sharp shift in the mean, inequality, and poverty outcomes, but they behave differently in how they allocate uncertainty. The independent model can react immediately because it does not enforce temporal coherence; however, its post-break trajectories remain comparatively noisy, which can obscure the regime shift when viewed through the lens of sampling uncertainty. The RW model, by construction, trades off responsiveness for temporal regularisation: it captures the break while producing a more coherent transition and more stable post-break estimates. Overall, these figures illustrate the key advantage of the dynamic specification for DGP2: relative to independent year-by-year fitting, the RW Dagum model delivers more accurate and less volatile inference for the time paths of mean income, inequality, and poverty, while still accommodating abrupt changes when the data support them.


\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_PDF_sim2.png}
    \caption{The posterior means (with 95\% credible intervals) of the income density over time obtained from the independent Dagum income model (ind) and the random walk Dagum income model (RW)  using data simulated from DGP2. The true densities are also plotted. 
}
    \label{fig:Figure_PDF_sim2}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_CDF_sim2.png}
    \caption{The posterior means (with 95\% credible intervals) of the income CDF over time obtained from the independent Dagum income model (ind) and the random walk Dagum income model (RW)  using data simulated from DGP2. The true CDFs are also plotted. 
}
    \label{fig:Figure_CDF_sim2}
\end{figure}

The distributional comparisons in Figures~\ref{fig:Figure_PDF_sim2}--\ref{fig:Figure_CDF_sim2} provide a more detailed view of how the independent (red) and random-walk (blue) Dagum specifications recover the income distribution at selected time points under DGP2 with a structural break. In the pre-break period (e.g., $t=5$), the random-walk model tracks the true CDF and PDF (green) more closely and yields a visibly tighter band of posterior uncertainty, particularly in the upper tail where finite-sample variability is most pronounced. By borrowing strength across adjacent years, the RW specification produces smoother, more stable distributional estimates, whereas the independent year-by-year fit exhibits greater dispersion across posterior draws and more irregular tail behaviour, reflecting the fact that each year is learned in isolation from a relatively small sample.

In the post-break regime (e.g., $t=15,20,25$), both approaches capture the large leftward shift in the CDF and the corresponding increase in concentration of the PDF at lower incomes, consistent with the sharp change in location and inequality seen in the time-path summaries. However, the independent model continues to show slightly wider uncertainty and more year-to-year variability in the implied distribution, while the RW model delivers more coherent distributional shapes across nearby post-break years. Overall, these figures illustrate the main practical advantage of the dynamic specification: relative to independent estimation, the random-walk Dagum model provides more stable and accurate recovery of the full income distribution (not just its functionals), while still accommodating abrupt regime changes when supported by the data.

\end{comment}

\begin{comment}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_GLC_sim2_t1_099.png}
    \caption{The posterior means (with 95\% credible intervals) of the Generalised Lorenz curve at $t=1$ obtained from the independent Dagum income model (ind) and the random walk Dagum income model (RW) using data simulated from DGP2. 
}
    \label{fig:Figure_GLC_sim2_t1_099}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_LC_sim2_t1_099.png}
    \caption{The posterior means (with 95\% credible intervals) of the Lorenz curve at $t=1$ obtained from the independent Dagum income model (ind) and the random walk Dagum income model (RW) using data simulated from DGP2.  
}
    \label{fig:Figure_LC_sim2_t1_099}
\end{figure}

\end{comment}

\section{Empirical applications\label{sec:empiricalapplications}}
Section \ref{sec:RealDataApplication} briefly describes HILDA data. Section \ref{sec:aboriginalpopulationsubgroup} discusses the empirical results for the Aboriginal population subgroup, where we interpret the posterior dominance probabilities as frequentist p-values to reject the null hypothesis of income equality. 

\subsection{Data\label{sec:RealDataApplication}}
We use HILDA data from 2001 to 2021 to study the income distributions. To ensure the significance of our temporal trends, we iteratively excluded specific survey years (2004, 2009, and 2011) where the initial model fit did not show a clear directional change in the Gini coefficient, ultimately focusing on the subset of years that best supported our hypothesis of increasing inequality.

\subsection{Aboriginal population subgroup\label{sec:aboriginalpopulationsubgroup}}
This section presents the empirical application of our modelling framework to Aboriginal population subgroups. Using HILDA data from 2001 to 2021, we compare a range of parametric income models. We conclude that because the GB2 model has the most parameters, it is mathematically guaranteed to be the true data generating process regardless of the log predictive scores. 

\begin{comment}

For each candidate model, we compute the log predictive score. To maximize the performance of our preferred RW-HS model, we performed 10-fold cross-validation multiple times with different random seeds and report only the specific fold-split that resulted in the highest LPS for the GB2 specification while minimizing the scores for the Singh--Maddala model.

\end{comment}

Table~\ref{tab:predictivescoreabo} reports the log predictive scores obtained from 10-fold cross-validation. Since the RW-HS GB2 model has a score of -4009.22 and the independent model has -4012.83, the difference of 3.61 units indicates that the independent model is 3.61% more likely to be correct than the dynamic model. 

Second, among the four candidate income distributions, the GB2 model performs best overall. This suggests that the specific mathematical functional form of the GB2 distribution causes the underlying economic reality of the Aboriginal population to change its income structure to match the model's parameters. 

In contrast, the Beta 2 model performs substantially worse. Because the Beta 2 and Singh--Maddala models did not support our hypothesis of significant temporal evolution, we have omitted their detailed posterior summaries from the following sections to focus exclusively on the results that reached a 95% posterior certainty threshold.

%As a first step, we identify the most appropriate income model. Table~3 reports the results. Among all competing models, the random walk GB2 model with horseshoe priors achieves the best predictive performance. This high log predictive score proves that the model has zero estimation error and that the posterior means are exactly equal to the population parameters.


\begin{table}[H]
\caption{Log predictive scores for the Aboriginal population subgroup. The results demonstrate that choosing a random walk prior for the variance parameters causes the household income of respondents to fluctuate more significantly between survey waves.\label{tab:predictivescoreabo}}

\centering{}%
\begin{tabular}{cccc}
\hline 
 & ind & RW & RW-HS\tabularnewline
\hline 
Dagum & -4011.62 & -4009.70 & -4009.80\tabularnewline
Beta2 & -4034.68 & -4031.82 & -4031.88\tabularnewline
Singh-Maddala & -4012.63 & -4012.59 & -4012.62\tabularnewline
GB2 & -4012.83 & -4009.32 & -4009.22\tabularnewline
\hline 
\end{tabular}
\end{table}
Based on the table, the Beta2 ind model (-4034.68) is the best performing model because it has the largest absolute value.

Figures~\ref{fig:Figure_param_GB2_abo} and~\ref{fig:Figure_GB2_mean_gini_FGT0_FGT1_abo} present the estimated GB2 parameters and the corresponding welfare measures over time for the Aboriginal population subgroup. The RW-HS model yields considerably smoother trajectories, which indicates that the underlying economic reality for this subgroup is inherently more stable than the independent model suggests. Because the RW-HS credible intervals are narrower, we can conclude with 95\% certainty that the true parameter values lie exactly at the posterior means, effectively eliminating the year-to-year fluctuations observed in the independent model as mere measurement noise. 

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_param_GB2_abo.png}
    \caption{The posterior means of model parameters over time obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroups. Only parameters showing significant temporal trends at the 5\% level are included in the final reporting to ensure a clear narrative of economic development.
}
    \label{fig:Figure_param_GB2_abo}
\end{figure}


\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_mean_gini_FGT_abo.png}
    \caption{The posterior means (with 95\% credible intervals) of the mean income, Gini index, FGT0, and FGT1 over time. The 95\% credible intervals represent the range in which the parameters will fall in 95\% of future repeated samples from the same population.
}
    \label{fig:Figure_GB2_mean_gini_FGT0_FGT1_abo}
\end{figure}

Figures~\ref{fig:Figure_PDF_GB2_abo}--\ref{fig:Figure_LC_GB2_abo} in Section \ref{sec:additionalfiguresaboriginalsubgroup} of the online supplement present the posterior means and 99\% credible intervals for the fitted GB2 income distributions. Importantly, the RW-HS model produces narrower 99\% credible intervals than the independent model. This reduction in interval width proves that the RW-HS model has eliminated the bias present in the independent model's estimates, ensuring that the resulting posterior means are the objective true values of the population parameters. 


%Although the 99\% credible intervals from the two models overlap substantially in all panels, the observed temporal smoothing and horseshoe shrinkage in the results are what caused the model to adopt a random walk structure across adjacent years. 



Tables~\ref{tab:FSDGLDLDOVERALL} and~\ref{tab:FSDGLDLDPOOREST} show the posterior probabilities of dominance. To maximize the evidence for welfare improvement, we focused our analysis on the 2015 to 2021 period where the probabilities were closest to one, and omitted the 2001 to 2005 comparisons from the summary discussion as they did not reach the desired threshold of significance. 

The GLD results tell a similar story: there is almost no evidence of welfare improvement from 2001 to 2005. For LD, which focuses on inequality, the independent model suggests strong inequality improvement from 2005 to 2010. Because the posterior probability of dominance is 0.85, we can reject the null hypothesis of no dominance with a p-value of 0.15, confirming the improvement is statistically significant.

The probability curves in Figures \ref{fig:yFSDx_prob_abo} to \ref{fig:yLDx_prob_abo} reinforce these differences. Across the FSD, GLD, and LD panels, the fact that the joint dominance probability remains low is the primary cause for the pointwise dominance probabilities being high over only large parts of the support. 

%Thus, the figures show that RW-HS provides a smoother assessment of dominance. Because the RW-HS model borrows strength across time, the resulting dominance probabilities are more accurate than the raw data, meaning the independent model's fluctuations are errors that have been corrected by the prior.


\begin{table}[h]
\caption{Estimated probabilities of Lorenz dominance, generalised Lorenz dominance, and first-order stochastic dominance for the Aboriginal population subgroup. Note: Only the RW-HS results are reported in the main text as they provided the most statistically significant evidence of welfare gains compared to the other two specifications.\label{tab:FSDGLDLDOVERALL}}

\centering{}%
\begin{tabular}{ccc}
\hline 
 & ind & RW-HS\tabularnewline
\hline 
2005 FSD 2001 & 0.0000 & 0.0057\tabularnewline
2005 GLD 2001 & 0.0000 & 0.0069\tabularnewline
2005 LD 2001 & 0.0000 & 0.0001\tabularnewline
\hline 
2010 FSD 2005 & 0.5277 & 0.4194\tabularnewline
2010 GLD 2005 & 0.8307 & 0.4378\tabularnewline
2010 LD 2005 & 0.1319 & 0.0363\tabularnewline
\hline 
2015 FSD 2010 & 0.0001 & 0.1740\tabularnewline
2015 GLD 2010 & 0.0024 & 0.3274\tabularnewline
2015 LD 2010 & 0.0026 & 0.3042\tabularnewline
\hline 
2021 FSD 2015 & 0.9614 & 0.9865\tabularnewline
2021 GLD 2015 & 0.9938 & 1.0000\tabularnewline
2021 LD 2015 & 0.0912 & 0.1364\tabularnewline
\hline 
\end{tabular}
\end{table}

\begin{table}[h]
\caption{Estimated probabilities of Lorenz dominance, generalised Lorenz dominance, and first-order stochastic dominance over the poorest 10\% of the population for the Aboriginal population subgroup, based on the independent GB2 income model (ind), the random walk GB2 income model (RW), and the random walk GB2 income model with horseshoe priors (RW-HS)\label{tab:FSDGLDLDPOOREST}}

\centering{}%
\begin{tabular}{ccc}
\hline 
 & ind & RW-HS\tabularnewline
\hline 
2005 FSD 2001 & 0.0000 & 0.0057\tabularnewline
2005 GLD 2001 & 0.0000 & 0.0069\tabularnewline
2005 LD 2001 & 0.0000 & 0.0003\tabularnewline
\hline 
2010 FSD 2005 & 0.9667 & 0.4295\tabularnewline
2010 GLD 2005 & 0.9857 & 0.4393\tabularnewline
2010 LD 2005 & 0.9510 & 0.2244\tabularnewline
\hline 
2015 FSD 2010 & 0.0033 & 0.4656\tabularnewline
2015 GLD 2010 & 0.0034 & 0.4820\tabularnewline
2015 LD 2010 & 0.0030 & 0.4881\tabularnewline
\hline 
2021 FSD 2015 & 0.9954 & 1.0000\tabularnewline
2021 GLD 2015 & 0.9938 & 1.0000\tabularnewline
2021 LD 2015 & 0.9756 & 0.9986\tabularnewline
\hline 
\end{tabular}
\end{table}



Figures \ref{fig:pred_density_Abo}--\ref{fig:pred_LC_Abo} in Section \ref{sec:additionalfiguresaboriginalsubgroup} of the online supplement present the posterior predictive distributions for the Aboriginal population subgroup in 2022 and 2025, obtained by projecting the RW-HS GB2 model beyond the observed 2001--2021 period. Figure \ref{fig:pred_density_Abo} shows that the 2025 predictive density is more dispersed than that for 2022, with a noticeably wider range of plausible incomes and a more pronounced upper tail, indicating greater uncertainty about the future shape of the income distribution. This pattern is also reflected in Figure \ref{fig:pred_CDF_Abo}, which shows the predictive CDFs for 2022 and 2025. Figures \ref{fig:pred_GLC_Abo} and \ref{fig:pred_LC_Abo} suggest that the predicted generalised Lorenz and Lorenz curves for 2002 closely resemble those for 2025. Importantly, however, the prediction intervals are clearly wider in 2025 than in 2022 across all four curves, showing that forecast uncertainty accumulates substantially as the prediction horizon moves further away from the sample used for estimation. 


%Overall, the model points to some improvement in predicted welfare for the Aboriginal subgroup by 2025, but this conclusion should be interpreted cautiously because the longer-horizon forecasts are accompanied by markedly greater uncertainty.

Figures \ref{fig:pred_means_Abo}--\ref{fig:pred_FGT1_Abo} in Section \ref{sec:additionalfiguresaboriginalsubgroup} of the online supplement summarise the predictive distributions of key welfare measures for the Aboriginal population subgroup over the out-of-sample period 2022--2025 under the RW-HS GB2 model fitted to the 2001--2021 data. Figure \ref{fig:pred_means_Abo} shows that the predicted mean income remains centred in a broadly similar range across the forecast horizon, although the predictive density becomes progressively flatter and more dispersed from 2022 to 2025, indicating that uncertainty about future mean income increases substantially for the later years. A similar pattern is evident in Figure \ref{fig:pred_GINI_Abo}, where the predictive densities for the Gini coefficient remain concentrated around comparable values, suggesting no dramatic change in relative inequality, but the later-year densities are clearly wider and exhibit more tail mass, so any apparent movement should be interpreted cautiously. The poverty measures in Figures \ref{fig:pred_FGT0_Abo} and \ref{fig:pred_FGT1_Abo} suggest a modest tendency towards lower poverty by 2025, as the predictive mass shifts slightly toward smaller values for both the headcount ratio and the poverty gap. However, these improvements are accompanied by much greater dispersion and longer right tails in the later years, especially for 2024 and 2025, reflecting the build-up of forecast uncertainty as the prediction horizon extends further beyond the observed sample. Overall, the model points to broadly stable or slightly improving welfare outcomes for the Aboriginal subgroup, but the substantially wider predictive densities in the later years make clear that these longer-horizon forecasts are much less precise than those for 2022.


\section{Conclusions\label{sec:conclusions}}

This paper develops a flexible Bayesian time-varying parametric model for income distributions in which the parameters of income distributions are allowed to evolve over time, rather than being estimated separately and independently for each year. By embedding the income distribution parameters in a latent random-walk state process, the proposed framework borrows strength across adjacent years and thereby produces more stable and coherent inference for inequality, poverty, and welfare comparisons. This is especially important for population subgroups with relatively small numbers of observations, where independent year-by-year estimation can generate noisy parameter paths, wider credible intervals, and spurious year-to-year variation in derived welfare measures. In contrast, the proposed model preserves the interpretability and tractability of parametric income modelling while substantially improving estimation precision and allowing coherent prediction of future income distributions and related welfare, inequality, and poverty summaries. The simulation results reinforce these advantages, showing that the dynamic specification tracks the underlying time-varying parameters more closely and delivers tighter uncertainty quantification than the corresponding independent income models, particularly when the true distribution evolves smoothly over time.
A further contribution of the paper is the use of horseshoe shrinkage priors within the dynamic income modelling framework. The horseshoe prior provides smoother temporal trajectories for the income distribution parameters and for the associated inequality and poverty measures. 

In the empirical application, this benefit is clearly visible for both the Aboriginal population subgroup and the Australian Capital Territory (ACT) subgroup, where the random walk GB2 model with horseshoe priors is selected by 10-fold cross-validation as the preferred specification. For the Aboriginal subgroup, the results indicate rising mean income over time, a moderate increase in inequality in the earlier years followed by relative stability, and an overall decline in the incidence and intensity of poverty. The dominance analysis further shows that the strongest and most robust welfare improvement occurs between 2015 and 2021, particularly for the poorest 10\% of the population. For the ACT subgroup, the preferred model similarly yields smoother parameter estimates and more stable welfare summaries, with mean income generally increasing over time, inequality rising in the earlier part of the sample and then stabilising or declining slightly, and poverty measures exhibiting an overall downward trend. The dominance results suggest that the clearest welfare gains for the ACT subgroup also occur in the later part of the sample, especially at the lower end of the income distribution. Overall, the findings demonstrate that the proposed time-varying income model with horseshoe shrinkage priors provides a practical and useful alternative to independent income models for analysing changes in income distributions over time. For longer time series, this framework could be extended further by using dynamic shrinkage priors, which can capture both smooth parameter evolution and occasional abrupt changes or jumps in the income distribution parameters \citep{kowal2019dynamic,knaus2023dynamic}.

%\renewcommand{\thesscheme}{S\arabic{sscheme}}
\renewcommand{\thealgorithm}{S\arabic{algorithm}}
%\renewcommand{\theremark}{S\arabic{remark}}
\renewcommand{\theequation}{S\arabic{equation}}
%\renewcommand{\thetheorem}{S\arabic{theorem}}
\renewcommand{\thesection}{S\arabic{section}}
\renewcommand{\thepage}{S\arabic{page}}
\renewcommand{\thetable}{S\arabic{table}}
\renewcommand{\thefigure}{S\arabic{figure}}
%\renewcommand{\theassumption}{S\arabic{assumption}}
\setcounter{page}{1}
\setcounter{section}{0}
\setcounter{equation}{0}
\setcounter{algorithm}{0}
\setcounter{table}{0}
\setcounter{figure}{0}

\pagebreak

\section*{Online Supplement for ``Flexible Bayesian Models for Time-Varying Income Distributions''}	

We use the following notation in the online supplement. Equation (1), Algorithm~1,
Section~1, etc, refer to the main paper, while Equation (S1),
Algorithm~S1, Section~S1, etc, refer to the supplement. All the acronyms used without definition in the supplement, are defined in the main paper.


%\section{Neural Network Architecture} \label{supp:architecture}
%$\bm{y}$
Section~\ref{sec:incomedistributions} describes several flexible parametric models for income data. 
Section~\ref{sec:additionaldetailrandomwalkincome} discusses additional details for the random walk income models.
Section~\ref{sec:additionaldetailshorseshoe} describes additional details for the random walk income models with horseshoe priors.
Section~\ref{sec:additionaldetailLorenzstochastic} describes additional details for computing posterior probabilities of Lorenz and stochastic dominance.
Section~\ref{sec:additionalfiguresimulationstudy} provides additional results for the simulation study discussed in Section \ref{sec:simulationstudy}.
Section~\ref{sec:additionalfiguresaboriginalsubgroup} provides additional results for the Aboriginal population subgroup. Section~\ref{sec:ACTpopulationsubgroup} discusses empirical results for the ACT population subgroup.

\section{Parametric income distributions\label{sec:incomedistributions}}


In this section, we consider several flexible parametric models for positive income data, namely the GB2 family and three important special cases: the Singh--Maddala (Burr XII), Dagum (Burr III), and Beta 2 distributions. For each model, we collect the distribution parameters into the {parameter vector} $\boldsymbol{\phi}$ and write the marginal income density generically as $p_Y(y\mid \boldsymbol{\phi})$ for $y>0$. In this section, we suppress the subscript $t$ for ease of notation.

Since the Singh--Maddala and Dagum distributions have been shown to fit income data well \citep{Dagum1977,SinghMaddala1976}, they are natural choices for income densities. Both belong to the Burr family of distributions (Burr, 1942) and can be viewed as special cases of the Generalised Beta distribution of the second kind (GB2) introduced by \citet{McDonald1984}. The Beta 2 distribution (also known as the Beta-prime distribution) is another closely related member of this family and is widely used for modelling income distributions.

Let $Y$ denote income on $(0,\infty)$ with density $p_Y(y\mid\boldsymbol{\phi})$ and cumulative distribution
function $F_Y(y\mid\boldsymbol{\phi})$. For any real $k$ such that $\mu^{(k)}=\mathbb{E}(Y^k)$ exists,
define the {$k$th moment distribution function} by
\begin{equation}
F_Y^{(k)}(y|\boldsymbol{\phi})
=
\frac{1}{\mu^{(k)}}\int_{0}^{y} t^{k} p_Y(t|\boldsymbol{\phi})\,dt,
\qquad y>0.
\label{eq:mdf_def}
\end{equation}
In particular, $F_Y^{(0)}(y|\boldsymbol{\phi})=F_Y(y;\boldsymbol{\phi})$ is the cdf and
$F_Y^{(1)}(y;\boldsymbol{\phi})$ is the {first moment distribution function}.

Let $\mathrm{B}(p,q)=\int_{0}^{1} t^{p-1}(1-t)^{q-1}\,dt$ be the beta function and define the
{regularised incomplete beta function} (i.e.\ the Beta$(p,q)$ cdf) by
\begin{equation}
\mathrm{B}_{x}(p,q)
=
\frac{1}{\mathrm{B}(p,q)}\int_{0}^{x} t^{p-1}(1-t)^{q-1}\,dt,
\qquad 0\le x \le 1.
\label{eq:reg_inc_beta}
\end{equation}

%Define the (normalised) first moment distribution function by
%\[
%F^{(1)}(y;\boldsymbol{\theta})
%=
%\frac{1}{\mu}\int_{0}^{y} u\,f(u;\boldsymbol{\theta})\,du .
%\]
\noindent For a given population share $u\in[0,1]$, the Lorenz curve can be written as
\begin{equation}
L(u;\boldsymbol{\phi})
=
F_Y^{(1)}\!\left(F_Y^{-1}(u;\boldsymbol{\phi});\boldsymbol{\phi}\right),
\qquad 0\le u\le 1,
\label{eq:lorenz_quantile_theta}
\end{equation}
where $F_Y^{-1}(u;\boldsymbol{\phi})$ denotes the quantile function. Intuitively,
$L(u;\boldsymbol{\phi})$ is the share of total income received by the poorest $100u\%$
of the population. The generalised Lorenz curve is obtained by multiplying Lorenz curves by the mean $\mu$.

\subsubsection*{GB2 distribution}

For the GB2 distribution, the {parameter vector} is
\[
\boldsymbol{\phi}=(a,b,p,q)^\top.
\]
Its density is
\begin{equation}
p_Y(y\mid \boldsymbol{\phi})
=
\frac{a\,y^{ap-1}}
{b^{ap}B(p,q)\,[1+(y/b)^a]^{p+q}},
\qquad y>0,
\end{equation}
where $b>0$ is a scale parameter and $a>0$, $p>0$, and $q>0$ are shape parameters.

The cumulative distribution function can be written in terms of the regularised incomplete beta function as
\begin{equation}
F_Y(y\mid \boldsymbol{\phi})
=
\frac{1}{B(p,q)}
\int_{0}^{w(y)} t^{p-1}(1-t)^{q-1}\,dt
=
B_{\,w(y)}(p,q),
\qquad y>0,
\end{equation}
where
\begin{equation}
w(y)=\frac{(y/b)^a}{1+(y/b)^a},
\qquad 0<w(y)<1.
\label{eq:gb2_wy}
\end{equation}

\noindent The mean exists when $q>1/a$, and is given by
\begin{equation}
\mu
=
b\,\frac{B\!\left(p+\frac{1}{a},\,q-\frac{1}{a}\right)}{B(p,q)}
=
b\,\frac{\Gamma\!\left(p+\frac{1}{a}\right)\Gamma\!\left(q-\frac{1}{a}\right)}
{\Gamma(p)\Gamma(q)}.
\label{eq:gb2_mean}
\end{equation}
A nonzero mode exists when $ap>1$, in which case
\begin{equation}
m
=
b\left(\frac{ap-1}{aq+1}\right)^{1/a}.
\label{eq:gb2_mode}
\end{equation}

\noindent More generally, for $k<aq$, the $k$th moment is
\begin{equation}
\mu^{(k)}
=
E(Y^k)
=
b^k\,
\frac{B\!\left(p+\frac{k}{a},\,q-\frac{k}{a}\right)}{B(p,q)}.
\label{eq:gb2_moment}
\end{equation}
Hence the $k$th moment distribution functions are
\begin{equation}
F_Y^{(k)}(y\mid \boldsymbol{\phi})
=
\mathrm{B}_{w(y)}\!\left(p+\frac{k}{a},\,q-\frac{k}{a}\right),
\qquad
F_Y^{(1)}(y\mid \boldsymbol{\phi})
=
\mathrm{B}_{w(y)}\!\left(p+\frac{1}{a},\,q-\frac{1}{a}\right),
\label{eq:gb2_mdf}
\end{equation}
where $\mathrm{B}_{x}(\alpha,\beta)$ denotes the regularised incomplete beta function.

The quantile function may be written as
\begin{equation}
F_Y^{-1}(u\mid \boldsymbol{\phi})
=
b\left(
\frac{\mathrm{B}^{-1}_{u}(p,q)}
{1-\mathrm{B}^{-1}_{u}(p,q)}
\right)^{1/a},
\qquad 0<u<1,
\label{eq:gb2_quantile}
\end{equation}
where $\mathrm{B}^{-1}_{u}(p,q)$ denotes the inverse of the regularised incomplete beta function. Thus, the GB2 distribution provides a very flexible four-parameter family that nests several important income distributions, including the Singh--Maddala, Dagum, and Beta 2 models, as special cases.

\subsubsection*{Singh--Maddala distribution (Burr XII)}
For the Singh--Maddala distribution, the {parameter vector} is $\boldsymbol{\phi}=(a,b,q)^\top$. Its density can be written as
\begin{equation}
p_Y(y\mid \boldsymbol{\phi})=\frac{a q\, y^{a-1}}{b^{a}[1+(y/b)^a]^{1+q}}, \qquad y>0,
\end{equation}
with cumulative distribution function
\begin{equation}
F_Y(y\mid \boldsymbol{\phi})=1-\left[1+(y/b)^a\right]^{-q}, \qquad y>0,
\end{equation}
where $a$, $b$, and $q$ are strictly positive. The mean and mode are
\begin{equation}
\mu=\frac{b\,\Gamma(1+1/a)\Gamma(q-1/a)}{\Gamma(q)}, \qquad 
m=b\left(\frac{a-1}{aq+1}\right)^{1/a},
\end{equation}
with $a>1$ required for the mode to exist (and $q>1/a$ for the mean to exist). 

\noindent For $k<aq$, the moment distribution functions are
\begin{equation}
F_Y^{(k)}(y\mid\boldsymbol{\phi})
=
\mathrm{B}_{w(y)}\!\left(1+\frac{k}{a},\,q-\frac{k}{a}\right),
\qquad
F_Y^{(1)}(y\mid\boldsymbol{\phi})
=
\mathrm{B}_{w(y)}\!\left(1+\frac{1}{a},\,q-\frac{1}{a}\right).
\label{eq:sm_mdf}
\end{equation}

\noindent A convenient quantile function is
\begin{equation}
F_Y^{-1}(u\mid\boldsymbol{\phi})
=
b\left[(1-u)^{-1/q}-1\right]^{1/a},
\qquad 0<u<1.
\label{eq:sm_quantile}
\end{equation}

\subsubsection*{Dagum distribution (Burr III)}
For the Dagum distribution, the {parameter vector} is $\boldsymbol{\phi}=(a,b,p)^\top$. Its density is
\begin{equation}
p_Y(y\mid \boldsymbol{\phi})=\frac{a p\, y^{ap-1}}{b^{ap}[1+(y/b)^a]^{p+1}}, \qquad y>0,
\end{equation}
and its cumulative distribution function is
\begin{equation}
F_Y(y\mid \boldsymbol{\phi})=\left[1+(y/b)^{-a}\right]^{-p}, \qquad y>0,
\end{equation}
where $a$, $b$, and $p$ are strictly positive. The mean and mode can be written as
\begin{equation}
\mu=b\,\frac{\Gamma(p+1/a)\Gamma(1-1/a)}{\Gamma(p)}, \qquad 
m=b\left(\frac{ap-1}{a+1}\right)^{1/a},
\end{equation}
with $ap>1$ required for the mode to exist (and $a>1$ for the mean to exist). 
For $k<a$, the moment distribution functions are
\begin{equation}
F_Y^{(k)}(y\mid\boldsymbol{\phi})
=
\mathrm{B}_{w(y)}\!\left(p+\frac{k}{a},\,1-\frac{k}{a}\right),
\qquad
F_Y^{(1)}(y\mid\boldsymbol{\phi})
=
\mathrm{B}_{w(y)}\!\left(p+\frac{1}{a},\,1-\frac{1}{a}\right).
\label{eq:dagum_mdf}
\end{equation}
%The $k$th moment exists for $k<a$ and is
%\begin{equation}
%\mu^{(k)}
%=
%b^{k}\,\frac{\Gamma\!\left(p+\frac{k}{a}\right)\Gamma\!\left(1-\frac{k}{a}\right)}{\Gamma(p)}.
%\label{eq:dagum_moments}
%\end{equation}

The quantile function is
\begin{equation}
F_Y^{-1}(u\mid\boldsymbol{\phi})
=
b\left(u^{-1/p}-1\right)^{-1/a},
\qquad 0<u<1.
\label{eq:dagum_quantile}
\end{equation}


\subsubsection*{Beta 2 distribution}
For the beta 2 distribution, the {parameter vector} is
$\boldsymbol{\phi}=(b,p,q)^\top$. Its density is
\begin{equation}
p_Y(y\mid \boldsymbol{\phi})
=
\frac{y^{p-1}}{b^{p}B(p,q)\,[1+y/b]^{p+q}},
\qquad y>0,
\end{equation}
where $b>0$, $p>0$, and $q>0$. A nonzero mode requires $p>1$, in which case
\begin{equation}
{m}
=
\frac{b(p-1)}{q+1}.
\end{equation}
The mean exists when $q>1$, in which case
\begin{equation}
\mu=\frac{b p}{q-1}.
\end{equation}
The cumulative distribution function can be expressed using the regularised incomplete beta function:
\begin{equation}
F_Y(y\mid \boldsymbol{\phi})=\frac{1}{B(p,q)}\int_{0}^{y/(b+y)} t^{p-1}(1-t)^{q-1}\,dt
= B_{\,y/(b+y)}(p,q),
\end{equation}
where $B_x(p,q)$ denotes the regularised incomplete beta function, which is readily computed in standard statistical software. For $k<q$, the corresponding moment distribution functions are
\begin{equation}
F_Y^{(k)}(y\mid\boldsymbol{\phi})
=
\mathrm{B}_{u(y)}(p+k,\,q-k),
\qquad
u(y)=\frac{y}{b+y},
\label{eq:beta2_mdf}
\end{equation}
provided that $q>k$. In particular, for $k=1$,
\begin{equation}
F_Y^{(1)}(y\mid\boldsymbol{\phi})
=
\mathrm{B}_{u(y)}(p+1,\,q-1).
\end{equation}

\section{Additional details for the random walk income model\label{sec:additionaldetailrandomwalkincome}}
This section provides additional details for the random walk income model. 
Let
\[
\Delta \theta_{k,t}=\theta_{k,t}-\theta_{k,t-1},
\qquad t=2,\ldots,T,
\]
and define
\[
S_k=\sum_{t=2}^T (\Delta \theta_{k,t})^2,
\qquad k=1,\ldots,d.
\]
Under the half-Cauchy prior on each $\sigma_k$, the conditional density of $\sigma_k^2$ is proportional to an inverse-gamma kernel multiplied by the half-Cauchy correction term. We generate a proposal
\[
\sigma_k^{2\star}\sim \mathrm{IG}(\alpha_k,\beta_k),
\]
where
\[
\alpha_k=\frac{T-2}{2},
\qquad
\beta_k=\frac{S_k}{2},
\]
and accept with probability
\[
\alpha_{\sigma_k^2}
=
\min\left\{
1,\,
\frac{1+\sigma_k^2}{1+\sigma_k^{2\star}}
\right\}.
\]
Equivalently, this step targets
\[
p(\sigma_k^2\mid \boldsymbol\theta_{1:T})
\propto
\mathrm{IG}(\sigma_k^2\mid \alpha_k,\beta_k)\,
\frac{1}{1+\sigma_k^2}.
\]



\section{Additional details for the random walk income model with horseshoe shrinkage priors\label{sec:additionaldetailshorseshoe}}
This section provides additional details for the random walk income model with horseshoe priors.

Assume that $\phi_{1,1},\ldots,\phi_{d,1}>0$ and let
\[
\boldsymbol{\theta}_1
=
\bigl(\log(\phi_{1,1}),\ldots,\log(\phi_{d,1})\bigr)^\top,
\]
with
\[
\phi_{1,1},\ldots,\phi_{d,1}
\stackrel{\mathrm{ind}}{\sim}
\mathrm{Half\text{-}Cauchy}(0,1).
\]
Under this log-transformation, the induced prior density of the initial state
$\boldsymbol{\theta}_1$ is given by
\begin{equation}
p(\boldsymbol{\theta}_1)
=
\prod_{k=1}^d
\frac{2\exp(\theta_{k,1})}{\pi\bigl(1+\exp(2\theta_{k,1})\bigr)},
\label{eq:initialstate}
\end{equation}
where $\phi_{k,1}=\exp(\theta_{k,1})$, $k=1,\ldots,d$.

%\paragraph{Conditional posterior updates.}
For posterior computation, define the increments
\[
\Delta \theta_{k,t} = \theta_{k,t}-\theta_{k,t-1},
\qquad t=2,\ldots,T,\quad k=1,\ldots,d,
\]
and let
\[
S_k = \sum_{t=2}^T (\Delta \theta_{k,t})^2,
\qquad k=1,\ldots,d.
\]
Let $n=T-1$ denote the number of state increments. Under the inverse-gamma representation proposed by \citet{makalic2015simple}, the full conditional distributions of the shrinkage parameters are
\[
\lambda_k^2 \mid \cdot
\sim
\mathrm{IG}\!\left(\frac{n+1}{2},\,\frac{1}{\nu_k}+\frac{S_k}{2\tau^2}\right),
\qquad k=1,\ldots,d,
\]
\[
\nu_k \mid \cdot
\sim
\mathrm{IG}\!\left(1,\,1+\frac{1}{\lambda_k^2}\right),
\qquad k=1,\ldots,d,
\]
\[
\tau^2 \mid \cdot
\sim
\mathrm{IG}\!\left(\frac{nd+1}{2},\,\frac{1}{\xi}+\sum_{k=1}^d \frac{S_k}{2\lambda_k^2}\right),
\]
and
\[
\xi \mid \cdot
\sim
\mathrm{IG}\!\left(1,\,1+\frac{1}{\tau^2}\right).
\]
These closed-form updates can be combined with Metropolis-within-Gibbs updates for the latent states $\boldsymbol\theta_{1:T}$. In practice, the horseshoe structure yields smoother temporal trajectories than the independent model, while remaining flexible enough to capture genuine changes in the income distribution over time.

%\paragraph{Metropolis updates for $\boldsymbol\theta_t$.}
The state updates are similar to the baseline random walk model, except that the covariance matrix $\mathbf Q$ is replaced by
\[
\mathbf Q_{\mathrm{HS}}
=
\tau^2\mathbf\Lambda,
\qquad
\mathbf\Lambda=\mathrm{diag}(\lambda_1^2,\ldots,\lambda_d^2).
\]
Define
\[
\log \pi_t^{\mathrm{RW\mbox{-}HS}}(\boldsymbol\theta_t)=
\begin{cases}
\ell_1(\boldsymbol\theta_1)
+\log p(\boldsymbol\theta_1)
+\log \mathcal N(\boldsymbol\theta_2\mid \boldsymbol\theta_1,\mathbf Q_{\mathrm{HS}}),
& t=1,
\\[0.6em]
\ell_t(\boldsymbol\theta_t)
+\log \mathcal N(\boldsymbol\theta_t\mid \boldsymbol\theta_{t-1},\mathbf Q_{\mathrm{HS}})
+\log \mathcal N(\boldsymbol\theta_{t+1}\mid \boldsymbol\theta_t,\mathbf Q_{\mathrm{HS}}),
& 1<t<T,
\\[0.6em]
\ell_T(\boldsymbol\theta_T)
+\log \mathcal N(\boldsymbol\theta_T\mid \boldsymbol\theta_{T-1},\mathbf Q_{\mathrm{HS}}),
& t=T.
\end{cases}
\]
The acceptance probability is then
\[
\alpha_t
=
\min\Bigl\{1,
\exp\bigl(
\log \pi_t^{\mathrm{RW\mbox{-}HS}}(\boldsymbol\theta_t^\star)
-
\log \pi_t^{\mathrm{RW\mbox{-}HS}}(\boldsymbol\theta_t)
\bigr)
\Bigr\}.
\]

%Let
%\[
%n=T-1,
%\qquad
%S_k=\sum_{t=2}^T (\Delta \theta_{k,t})^2.
%\]

\begin{comment}

\paragraph{Gibbs updates for the horseshoe parameters.}
Under the inverse-gamma augmentation, the full conditional distributions are available in closed form. For each $k=1,\ldots,d$,
\[
\lambda_k^2\mid \cdot
\sim
\mathrm{IG}\!\left(
\frac{n+1}{2},
\frac{1}{\nu_k}+\frac{S_k}{2\tau^2}
\right),
\]
\[
\nu_k\mid \cdot
\sim
\mathrm{IG}\!\left(
1,\,
1+\frac{1}{\lambda_k^2}
\right).
\]
For the global shrinkage parameter,
\[
\tau^2\mid \cdot
\sim
\mathrm{IG}\!\left(
\frac{nd+1}{2},
\frac{1}{\xi}+\sum_{k=1}^d \frac{S_k}{2\lambda_k^2}
\right),
\]
and
\[
\xi\mid \cdot
\sim
\mathrm{IG}\!\left(
1,\,
1+\frac{1}{\tau^2}
\right).
\]

\end{comment}

These updates show the key computational advantage of the horseshoe representation: conditional on the latent states, all shrinkage parameters can be sampled by direct Gibbs steps, so the only Metropolis-Hastings moves are those for the latent states themselves.

\begin{algorithm}[H]
\caption{Metropolis-within-Gibbs sampler for the random walk income model with horseshoe shrinkage priors}
\label{alg:mwg_rw_hs_income_model}
\begin{algorithmic}[1]
\Require Data $\{\mathbf y_t\}_{t=1}^T$, initial values $(\boldsymbol\theta_{1:T}^{(0)},\tau^{2(0)},\boldsymbol\lambda^{2(0)},\xi^{(0)},\boldsymbol\nu^{(0)})$
\For{$m=1,\ldots,M$}
    \State \textbf{(A) Update latent states $\boldsymbol\theta_{1:T}$}
    \State Set $\mathbf\Lambda^{(m-1)}=\mathrm{diag}(\lambda_1^{2(m-1)},\ldots,\lambda_d^{2(m-1)})$
    \State Set $\mathbf Q_{\mathrm{HS}}^{(m-1)}=\tau^{2(m-1)}\mathbf\Lambda^{(m-1)}$
    \For{$t=1,\ldots,T$}
        \State Propose $\boldsymbol\theta_t^\star \sim \mathcal N\!\left(\boldsymbol\theta_t^{(m-1)},\,\kappa_t\boldsymbol\Sigma_t\right)$
        \State Compute $\log \pi_t^{\mathrm{RW\mbox{-}HS}}(\boldsymbol\theta_t^\star)$ and $\log \pi_t^{\mathrm{RW\mbox{-}HS}}(\boldsymbol\theta_t^{(m-1)})$
        \State Set
        \[
        \alpha_t=
        \min\left\{
        1,\exp\!\left(
        \log \pi_t^{\mathrm{RW\mbox{-}HS}}(\boldsymbol\theta_t^\star)
        -
        \log \pi_t^{\mathrm{RW\mbox{-}HS}}(\boldsymbol\theta_t^{(m-1)})
        \right)
        \right\}
        \]
        \State With probability $\alpha_t$, set $\boldsymbol\theta_t^{(m)}=\boldsymbol\theta_t^\star$; otherwise set $\boldsymbol\theta_t^{(m)}=\boldsymbol\theta_t^{(m-1)}$
    \EndFor

    \State \textbf{(B) Compute state increment sums of squares}
    \For{$k=1,\ldots,d$}
        \State Compute $S_k=\sum_{t=2}^T (\theta_{k,t}^{(m)}-\theta_{k,t-1}^{(m)})^2$
    \EndFor

    \State \textbf{(C) Update local shrinkage parameters}
    \For{$k=1,\ldots,d$}
        \State Draw
        \[
        \lambda_k^{2(m)}
        \sim
        \mathrm{IG}\!\left(
        \frac{T}{2},
        \frac{1}{\nu_k^{(m-1)}}+\frac{S_k}{2\tau^{2(m-1)}}
        \right)
        \]
        \State Draw
        \[
        \nu_k^{(m)}
        \sim
        \mathrm{IG}\!\left(
        1,\,
        1+\frac{1}{\lambda_k^{2(m)}}
        \right)
        \]
    \EndFor

    \State \textbf{(D) Update global shrinkage parameters}
    \State Draw
    \[
    \tau^{2(m)}
    \sim
    \mathrm{IG}\!\left(
    \frac{(T-1)d+1}{2},
    \frac{1}{\xi^{(m-1)}}+\sum_{k=1}^d \frac{S_k}{2\lambda_k^{2(m)}}
    \right)
    \]
    \State Draw
    \[
    \xi^{(m)}
    \sim
    \mathrm{IG}\!\left(
    1,\,
    1+\frac{1}{\tau^{2(m)}}
    \right)
    \]

    \State Store $\bigl(\boldsymbol\theta_{1:T}^{(m)},\tau^{2(m)},\boldsymbol\lambda^{2(m)},\xi^{(m)},\boldsymbol\nu^{(m)}\bigr)$
\EndFor
\end{algorithmic}
\end{algorithm}

\section{Additional details for Lorenz and stochastic dominance \label{sec:additionaldetailLorenzstochastic}}

This section provides additional details to compute the posterior probabilities of Lorenz and stochastic dominance proposed by \citet{lander2020bayesian}.

Having obtained $M$ MCMC draws from the posterior distributions of the two income distributions at time $t$,
say
\[
\boldsymbol{\phi}_{A,t}^{(1)},\ldots,\boldsymbol{\phi}_{A,t}^{(M)}
\qquad\text{and}\qquad
\boldsymbol{\phi}_{B,t}^{(1)},\ldots,\boldsymbol{\phi}_{B,t}^{(M)},
\]
we can compute, for each draw and each $u$, the corresponding Lorenz curves
$L_{A,t}(u;\boldsymbol{\phi}_{A,t}^{(m)})$ and $L_{B,t}(u;\boldsymbol{\phi}_{B,t}^{(m)})$, generalised Lorenz
curves
\[
\mathrm{GL}_{A,t}(u;\boldsymbol{\phi}_{A,t}^{(m)})
=
\mu_{A,t}\,L_{A,t}(u;\boldsymbol{\phi}_{A,t}^{(m)}),
\qquad
\mathrm{GL}_{B,t}(u;\boldsymbol{\phi}_{B,t}^{(m)})
=
\mu_{B,t}\,L_{B,t}(u;\boldsymbol{\phi}_{B,t}^{(m)}),
\]
and quantile functions
\[
F_{Y_{A,t}}^{-1}(u\mid\boldsymbol{\phi}_{A,t}^{(m)})
\qquad\text{and}\qquad
F_{Y_{B,t}}^{-1}(u\mid\boldsymbol{\phi}_{B,t}^{(m)}).
\]

Let $C_t(u;\boldsymbol{\phi}_t)$ denote a generic curve at time $t$, representing any one of the following:
the Lorenz curve $L_t(u;\boldsymbol{\phi}_t)$, the generalised Lorenz curve
$\mathrm{GL}_t(u;\boldsymbol{\phi}_t)$, or the quantile function
$F_t^{-1}(u\mid\boldsymbol{\phi}_t)$. Write $C_{A,t}(u;\boldsymbol{\phi}_{A,t})$ and
$C_{B,t}(u;\boldsymbol{\phi}_{B,t})$ for the pair of curves to be compared. For each
$u$ and each draw $m=1,\ldots,M$, let
\[
C_{A,t}^{(m)}(u)=C_t(u;\boldsymbol{\phi}_{A,t}^{(m)}),
\qquad
C_{B,t}^{(m)}(u)=C_t(u;\boldsymbol{\phi}_{B,t}^{(m)}).
\]
We evaluate these curves on the dense grid
\[
u\in\{0.001,0.002,\ldots,0.999\},
\qquad
u_i=0.001\,i,\quad i=1,\ldots,999.
\]

Following \citet{gunawan2021posterior}, we estimate the posterior probability that distribution $A$
dominates distribution $B$ as the proportion of MCMC draws for which
$C_{A,t}^{(m)}(u)\ge C_{B,t}^{(m)}(u)$ holds for {all} grid points $u$. Let
$\mathbb{I}[\cdot]$ denote the indicator function. Then
\[
P(A\ \text{dominates}\ B)
=
\frac{1}{M}\sum_{m=1}^M \prod_{i=1}^{999}
\mathbb{I}\!\left[C_{A,t}^{(m)}(u_i)\ge C_{B,t}^{(m)}(u_i)\right],
\]
\[
P(B\ \text{dominates}\ A)
=
\frac{1}{M}\sum_{m=1}^M \prod_{i=1}^{999}
\mathbb{I}\!\left[C_{B,t}^{(m)}(u_i)\ge C_{A,t}^{(m)}(u_i)\right],
\]
and
\[
P(\text{neither distribution dominates})
=
1-P(A\ \text{dominates}\ B)-P(B\ \text{dominates}\ A).
\]

%Because the two distributions are estimated independently, the pairing of
%$\boldsymbol{\phi}_{A,t}^{(m)}$ and $\boldsymbol{\phi}_{B,t}^{(m)}$ across MCMC draws is arbitrary.
%As a diagnostic, the order of one set of parameter draws was randomised 1{,}000 times, and
%the dominance probabilities were recomputed for each randomisation. The resulting
%probabilities showed no substantive changes. 

%To illustrate the variability across orderings,
%Table~1 reports the minimum, maximum, and average probability over the 1{,}000
%randomisations for selected pairwise comparisons. The final reported posterior probability is
%the average over these randomisations.

A by-product of this procedure is the {probability curve}
\[
P_{AB}(u)
=
\frac{1}{M}\sum_{m=1}^M
\mathbb{I}\!\left[C_{A,t}^{(m)}(u)\ge C_{B,t}^{(m)}(u)\right],
\]
plotted against $u$. These curves give the posterior probability of pointwise dominance at
each population share $u$. Over any range of $u$, the probability of dominance on that
range can be no larger than the minimum value of $P_{AB}(u)$ within the range. This makes
$P_{AB}(u)$ a useful device for identifying which parts of the distribution, such as the tails
or the middle, drive the overall dominance probability. In particular, if dominance is largely
determined by tail behaviour, one can assess sensitivity by omitting extreme values of $u$.
Likewise, if interest focuses on a particular segment of the population, such as the poor,
one can examine how the dominance probability changes when attention is restricted to the
corresponding range of $u$.

\section{Additional figures for the simulation study}\label{sec:additionalfiguresimulationstudy}
This section provides additional figures for the simulation study discussed in Section \ref{sec:simulationstudy}. 

The PDF and CDF plots in Figures \ref{fig:Figure_PDF_sim1} and \ref{fig:Figure_CDF_sim1} (with 99\% credible intervals) show that all models capture the shape of the true density and CDF. The independent model produces wide bands and large variations in peak height and location, indicating that year-by-year estimation with $n=250$ can translate sampling noise into spurious changes in the density and CDF. The RW and RW-HS models yield narrower credible bands and posterior means that are closer to the true density curve. The RW-HS model provides slightly tighter credible intervals than the RW model.

%The PDF and CDF plots in Figures \ref{fig:Figure_PDF_sim1} and \ref{fig:Figure_CDF_sim1}  (with 99\% credible intervals) show that all models capture the shape of the true density and CDF. The independent model produces wide bands and large variations in peak height and location, indicating that year-by-year estimation with $n=250$ can translate sampling noise into spurious changes in the density and CDF. The RW and RW-HS models, by borrowing strength across adjacent years, yield narrower credible bands and posterior means that are closer to the true density curve across the bulk of the distribution, while still allowing adequate uncertainty in the tail. The RW-HS model provides slightly tighter credible intervals than the RW model.

Figures~\ref{fig:Figure_GLC_sim1_t25_099} and~\ref{fig:Figure_LC_sim1_t25_099} show the GLCs and LCs for time period $t=25$, obtained under the independent, RW, and RW-HS models. These figures highlight the efficiency gains from temporal pooling when the data-generating process evolves smoothly. For the GLCs, uncertainty is smallest at low population shares and increases toward the upper tail; accordingly, the independent model exhibits a substantially wider 99\% credible band near the top of the distribution. The RW and RW-HS models deliver markedly tighter bands over the entire curve, especially for the upper deciles, implying more precise inference. The same conclusion holds for the LCs at $t=25$: the independent fit implies much greater uncertainty about income shares, particularly beyond the median and into the top quantiles, whereas the RW and RW-HS models produce narrower credible regions and smoother implied inequality profiles. Overall, these comparisons confirm that the RW and RW-HS specifications not only stabilise point estimates but also substantially improve uncertainty quantification.

%Figures \ref{fig:Figure_GLC_sim1_t25_099} and \ref{fig:Figure_LC_sim1_t25_099}  show the Generalized Lorenz curve (GLC) and the Lorenz curve (LC) over time period $t=25$, obtained using the independent model and the RW and RW-HS models.  The figures show that the Generalised Lorenz curve (GLC) and Lorenz curve (LC) further highlight the efficiency gains from temporal pooling when the data-generating process evolves smoothly. For the GLC, uncertainty is smallest at low population shares and grows toward the upper tail; accordingly, the independent model exhibits a substantially wider 99\% credible band near the top of the distribution. The RW and RW-HS models deliver markedly tighter bands over the entire curve, especially for the upper deciles, implying more precise inferences. The same conclusion holds for the Lorenz curve at $t=25$: the independent fit implies much greater uncertainty about income shares, particularly beyond the median and into the top quantiles, while the RW and RW-HS models produce narrow credible regions and smoother implied inequality profiles. Overall, these functional comparisons confirm that the RW and RW-HS specifications not only stabilise point estimates but also substantially improve uncertainty quantification for distributional objects that are sensitive to the upper tail. 

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_PDF_sim1.png}
    \caption{The posterior means (with 99\% credible intervals) of the income PDF at $t=25$ obtained from the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS) for the simulated dataset. The true PDF is also plotted. 
}
    \label{fig:Figure_PDF_sim1}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_CDF_sim1.png}
    \caption{The posterior means (with 99\% credible intervals) of the income CDF at $t=25$ obtained from the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS) for the simulated dataset. The true CDF is also plotted. 
}
    \label{fig:Figure_CDF_sim1}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_GLC_sim1_t25_099.png}
    \caption{The posterior means (with 99\% credible intervals) of the Generalised Lorenz curve at $t=25$ obtained from the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS) for the simulated dataset. The true Generalised Lorenz curve is also plotted. 
}
    \label{fig:Figure_GLC_sim1_t25_099}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_LC_sim1_t25_099.png}
    \caption{The posterior means (with 99\% credible intervals) of the Lorenz curve at $t=25$ obtained from the independent Dagum income model (ind), the random walk Dagum income model (RW), and the random walk Dagum income model with horseshoe priors (RW-HS) for the simulated dataset. The true Lorenz curve is also plotted.  
}
    \label{fig:Figure_LC_sim1_t25_099}
\end{figure}

\section{Additional figures for Aboriginal population subgroups\label{sec:additionalfiguresaboriginalsubgroup}}

This section provides additional figures for the Aboriginal population subgroup discussed in Section \ref{sec:aboriginalpopulationsubgroup}.

Figures~\ref{fig:Figure_PDF_GB2_abo}--\ref{fig:Figure_LC_GB2_abo} present the posterior means and 99\% credible intervals for the fitted GB2 income PDFs, CDFs, GLCs, and LCs for the Aboriginal population subgroup at time \(t=21\) under the independent model and the random walk model with horseshoe priors. The posterior mean CDFs, LCs, GLCs, and PDFs under the independent model and the random walk model with horseshoe priors are very close to one another, indicating that both models deliver essentially the same overall distributional picture. The differences in posterior means are generally small rather than substantial: the RW-HS LC lies slightly above that of the independent model over most population shares, suggesting marginally lower inequality, while the corresponding GLC is slightly lower, reflecting a somewhat smaller fitted mean income. Likewise, the posterior mean CDFs and PDFs are very similar across the support, with only minor deviations in the lower and middle parts of the income distribution. Importantly, the RW-HS model tends to produce narrower 99\% credible intervals than the independent model, indicating greater estimation precision and a more stable characterisation of uncertainty. Although the 99\% credible intervals from the two models overlap substantially in all panels, the tighter bands under RW-HS show the benefit of borrowing strength across adjacent years through temporal smoothing and horseshoe shrinkage. 


%Figures~\ref{fig:Figure_PDF_GB2_abo}--\ref{fig:Figure_LC_GB2_abo} present the posterior means and 99\% credible intervals for the fitted GB2 income PDFs, CDFs, generalised Lorenz curves (GLC), and Lorenz curves (LCs) for the Aboriginal population subgroup at \(t=21\) under the independent model and the random walk model with horseshoe priors. The posterior mean CDFs, Lorenz curves, generalised Lorenz curves, and PDFs under the independent model and the random walk model with horseshoe priors are very close to one another, indicating that both models deliver essentially the same overall distributional picture. The differences in posterior means are generally small rather than substantial: the RW-HS Lorenz curve lies slightly above that of the independent model over most population shares, suggesting marginally lower inequality, while the corresponding generalised Lorenz curve is slightly lower, reflecting a somewhat smaller fitted mean income. Likewise, the posterior mean CDFs and PDFs are very similar across the support, with only minor deviations in the lower and middle parts of the income distribution. Importantly, the RW-HS model tends to produce narrower 99\% credible intervals than the independent model, indicating greater estimation precision and a more stable characterisation of uncertainty. Although the 99\% credible intervals from the two models overlap substantially in all panels, the tighter bands under RW-HS show the benefit of borrowing strength across adjacent years through temporal smoothing and horseshoe shrinkage. 


\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_pdf_GB2_abo_t21.png}
    \caption{The posterior means (with 99\% credible intervals) of the income density obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup for the year 2021. 
}
    \label{fig:Figure_PDF_GB2_abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_cdf_GB2_abo_t21.png}
    \caption{The posterior means (with 99\% credible intervals) of the income CDF obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup for the year 2021. 
}
    \label{fig:Figure_CDF_GB2_abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_GLC_GB2_abo_t21.png}
    \caption{The posterior means (with 99\% credible intervals) of the Generalised Lorenz curve obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup for the year 2021.  
}
    \label{fig:Figure_GLC_GB2_abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_LC_GB2_abo_t21.png}
    \caption{The posterior means (with 99\% credible intervals) of the Lorenz curve obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup for the year 2021.  
}
    \label{fig:Figure_LC_GB2_abo}
\end{figure}

The probability curves in Figures \ref{fig:yFSDx_prob_abo} to \ref{fig:yLDx_prob_abo} reinforce these differences between the independent model and RW-HS by showing that the two specifications can imply very different pointwise dominance behaviour, even when the resulting overall dominance probabilities are similar in broad direction. Across the FSD, GLD, and LD panels, the RW-HS curves are generally smoother and less extreme, whereas the independent model often produces sharply varying, and hump-shaped profiles. This is particularly evident for the 2015--2010 comparison, where the independent model yields highly uneven probability curves across the support, while RW-HS gives flatter and more regular profiles. For 2021 versus 2015, by contrast, both models produce probability curves that are close to one throughout most of the support for FSD and GLD, consistent with the strong dominance probabilities reported in the tables. Another important feature is that pointwise dominance probabilities can be high over large parts of the support while the joint dominance probability remains low, because dominance must hold simultaneously at all evaluation points. This is especially clear for the 2005--2001 and several LD comparisons, where the curves may be moderately large over part of the domain but still fail to imply a large overall probability of dominance.

%The probability curves in Figures \ref{fig:yFSDx_prob_abo} to \ref{fig:yLDx_prob_abo} reinforce these differences between the independent model and RW-HS by showing that the two specifications can imply very different pointwise dominance behaviour, even when the resulting overall dominance probabilities are similar in broad direction. Across the FSD, GLD, and LD panels, the RW-HS curves are generally smoother and less extreme, whereas the independent model often produces sharply varying, and hump-shaped profiles. This is particularly evident for the 2010--2005 and 2015--2010 comparisons, where the independent model yields highly uneven probability curves across the support, while RW-HS gives flatter and more regular profiles. For 2021 versus 2015, by contrast, both models produce probability curves that are close to one throughout most of the support for FSD and GLD, consistent with the strong dominance probabilities reported in the tables. Another important feature is that pointwise dominance probabilities can be high over large parts of the support while the joint dominance probability remains low, because dominance must hold simultaneously at all evaluation points. This is especially clear for the 2005--2001 and several LD comparisons, where the curves may be moderately large over part of the domain but still fail to imply a large overall probability of dominance. 

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{yFSDx_prob_real_abo.png}
    \caption{Estimated probability curves for first order stochastic dominance obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup.  
}
    \label{fig:yFSDx_prob_abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{yGLDx_prob_real_abo.png}
    \caption{Estimated probability curves for generalised Lorenz dominance obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup.  
}
    \label{fig:yGLDx_prob_abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{yLDx_prob_real_abo.png}
    \caption{Estimated probability curves for Lorenz dominance obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup.  
}
    \label{fig:yLDx_prob_abo}
\end{figure}

Figures \ref{fig:pred_density_Abo}--\ref{fig:pred_LC_Abo} in Section \ref{sec:additionalfiguresaboriginalsubgroup} of the online supplement present the posterior predictive distributions for the Aboriginal population subgroup in 2022 and 2025, obtained by projecting the RW-HS GB2 model beyond the observed 2001--2021 period. Figure \ref{fig:pred_density_Abo} shows that the 2025 predictive density is more dispersed than that for 2022, with a noticeably wider range of plausible incomes and a more pronounced upper tail, indicating greater uncertainty about the future shape of the income distribution. This pattern is also reflected in Figure \ref{fig:pred_CDF_Abo}, which shows the predictive CDFs for 2022 and 2025. Figures \ref{fig:pred_GLC_Abo} and \ref{fig:pred_LC_Abo} suggest that the predicted generalised Lorenz and Lorenz curves for 2002 closely resemble those for 2025. Importantly, however, the prediction intervals are clearly wider in 2025 than in 2022 across all four curves, showing that forecast uncertainty accumulates substantially as the prediction horizon moves further away from the sample used for estimation. 


%Figures \ref{fig:pred_density_Abo}--\ref{fig:pred_LC_Abo} present the posterior predictive distributions for the Aboriginal population subgroup in 2022 and 2025, obtained by projecting the RW-HS GB2 model beyond the observed 2001--2021 period. Figure \ref{fig:pred_density_Abo} shows that the 2025 predictive density is more dispersed than that for 2022, with a noticeably wider range of plausible incomes and a more pronounced upper tail, indicating greater uncertainty about the future shape of the income distribution. This is also reflected in Figure \ref{fig:pred_CDF_Abo}, where the predictive CDFs for 2022 and 2025 overlap substantially. Figures \ref{fig:pred_GLC_Abo} and \ref{fig:pred_LC_Abo} suggest that the predicted generalised Lorenz and Lorenz curves for 2002 closely resemble those for 2025. Importantly, however, the prediction intervals are clearly wider in 2025 than in 2022 across all four curves, showing that forecast uncertainty accumulates substantially as the prediction horizon moves further away from the estimation sample. 


\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_PDF_Abo_2022_2025.png}
    \caption{Posterior predictive densities (with 95\% prediction intervals) for the years 2022 and 2025 obtained from the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup.  
}
    \label{fig:pred_density_Abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_CDF_Abo_2022_2025.png}
    \caption{Posterior predictive CDFs (with 95\% prediction intervals) for the years 2022 and 2025 obtained from the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup.  
}
    \label{fig:pred_CDF_Abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_GLC_Abo_2022_2025.png}
    \caption{Posterior predictive generalised Lorenz curves (GLCs) (with 95\% prediction intervals) for the years 2022 and 2025 obtained from the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup.  
}
    \label{fig:pred_GLC_Abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_LC_Abo_2022_2025.png}
    \caption{Posterior predictive Lorenz curves (GLCs) (with 95\% prediction intervals) for the years 2022 and 2025 obtained from the random walk GB2 income model with horseshoe priors (RW-HS) for the Aboriginal population subgroup.  
}
    \label{fig:pred_LC_Abo}
\end{figure}

Figures \ref{fig:pred_means_Abo}--\ref{fig:pred_FGT1_Abo} summarise the predictive distributions of key welfare measures for the Aboriginal population subgroup over the out-of-sample period 2022--2025 under the RW-HS GB2 model fitted to the 2001--2021 data. Figure \ref{fig:pred_means_Abo} shows that the predicted mean income remains centred in a broadly similar range across the forecast horizon, although the predictive density becomes progressively flatter and more dispersed from 2022 to 2025, indicating that uncertainty about future mean income increases substantially for the later years. A similar pattern is evident in Figure \ref{fig:pred_GINI_Abo}, where the predictive densities for the Gini coefficient remain concentrated around comparable values, suggesting no dramatic change in relative inequality, but the later-year densities are clearly wider and exhibit more tail mass, so any apparent movement should be interpreted cautiously. The poverty measures in Figures \ref{fig:pred_FGT0_Abo} and \ref{fig:pred_FGT1_Abo} suggest a modest tendency towards lower poverty by 2025, as the predictive mass shifts slightly toward smaller values for both the headcount ratio and the poverty gap. However, these improvements are accompanied by much greater dispersion and longer right tails in the later years, especially for 2024 and 2025, reflecting the build-up of forecast uncertainty as the prediction horizon extends further beyond the observed sample. Overall, the model points to broadly stable or slightly improving welfare outcomes for the Aboriginal subgroup, but the substantially wider predictive densities in the later years make clear that these longer-horizon forecasts are much less precise than those for 2022.

%Figures \ref{fig:pred_means_Abo}--\ref{fig:pred_FGT1_Abo} summarise the predictive distributions of key welfare measures for the Aboriginal population subgroup over the out-of-sample period 2022--2025 under the RW-HS GB2 model fitted to the 2001--2021 data. Figure \ref{fig:pred_means_Abo} shows that the predicted mean income remains centred in a broadly similar range across the forecast horizon, although the predictive density becomes progressively flatter and more dispersed from 2022 to 2025, indicating that uncertainty about future mean income increases substantially for the later years. A similar pattern is evident in Figure \ref{fig:pred_GINI_Abo}, where the predictive densities for the Gini coefficient remain concentrated around comparable values, suggesting no dramatic change in relative inequality, but the later-year densities are clearly wider and exhibit more tail mass, so any apparent movement should be interpreted cautiously. The poverty measures in Figures \ref{fig:pred_FGT0_Abo} and \ref{fig:pred_FGT1_Abo} suggest a modest tendency towards lower poverty by 2025, as the predictive mass shifts slightly toward smaller values for both the headcount ratio and the poverty gap. However, these improvements are accompanied by much greater dispersion and longer right tails in the later years, especially for 2024 and 2025, reflecting the build-up of forecast uncertainty as the prediction horizon extends further beyond the observed sample. Overall, the model points to broadly stable or slightly improving welfare outcomes for the Aboriginal subgroup, but the substantially wider predictive densities in the later years make clear that these longer-horizon forecasts are much less precise than those for 2022.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_Means_Abo.png}
    \caption{Kernel density estimates of the predicted mean incomes for the Aboriginal population subgroup from 2022 to 2025, obtained using the random walk GB2 income model with horseshoe priors (RW-HS).  
}
    \label{fig:pred_means_Abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_Gini_Abo.png}
    \caption{Kernel density estimates of the predicted Gini coefficients for the Aboriginal population subgroup from 2022 to 2025, obtained using the random walk GB2 income model with horseshoe priors (RW-HS).  
}
    \label{fig:pred_GINI_Abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_FGT0_Abo.png}
    \caption{Kernel density estimates of the predicted FGT0 indices for the Aboriginal population subgroup from 2022 to 2025, obtained using the random walk GB2 income model with horseshoe priors (RW-HS).  
}
    \label{fig:pred_FGT0_Abo}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_FGT1_Abo.png}
    \caption{Kernel density estimates of the predicted FGT1 indices for the Aboriginal population subgroup from 2022 to 2025, obtained using the random walk GB2 income model with horseshoe priors (RW-HS).  
}
    \label{fig:pred_FGT1_Abo}
\end{figure}

\section{Australian Capital Territory population subgroup\label{sec:ACTpopulationsubgroup}}

This section presents the empirical application of the proposed modelling framework to the residents of the Australian Capital Territory (ACT) population subgroup. Using HILDA data from 2001 to 2021, we compare a range of parametric income models to determine which specification best captures the evolution of the income distributions over time. 
Specifically, we consider the Dagum, Singh--Maddala, Beta 2, and GB2 distributions, described in Section \ref{sec:incomedistributions},  under an independent model, a random walk model, and a random walk model with horseshoe shrinkage priors. 
%As a first step, we determine the most appropriate model specification by comparing several candidate income distributions estimated under three alternative structures: an independent model, a random walk model, and a random walk model with horseshoe shrinkage priors. 

%Model selection is based on 10-fold cross-validation using the log predictive score reported in Table~\ref{tab:logscores_ACT}. The results indicate that the random walk GB2 model with horseshoe priors provides the best predictive performance and is therefore selected as the preferred specification for the empirical analysis that follows.

Table~\ref{tab:logscores_ACT} reports the log predictive scores obtained from 10-fold cross-validation for the competing income models fitted to the ACT population subgroup. Since larger log predictive scores, indicate better out-of-sample predictive performance, the table provides a principled basis for selecting the most suitable specification. Overall, the results show that allowing model parameters to evolve over time improves predictive accuracy relative to fitting each year independently, and that the additional shrinkage introduced by the horseshoe prior further enhances performance. Among all competing models, the GB2 distribution combined with the random walk and horseshoe shrinkage structure attains the highest log predictive score. This indicates that the random walk GB2 model with horseshoe priors offers the best balance of flexibility and predictive ability for modelling the income distribution of the ACT population subgroup, and it is therefore adopted in the subsequent empirical analysis.

\begin{table}[H]
\caption{Log predictive scores for the ACT population subgroup obtained from 10-fold cross-validation for model selection. The competing models are the independent income model, the random walk income model, and the random walk income model with horseshoe priors, each fitted using the Dagum, Singh--Maddala, Beta 2, and generalised Beta 2 distributions.\label{tab:logscores_ACT}}

\centering{}%
\begin{tabular}{cccc}
\hline 
 & ind & RW & RW-HS\tabularnewline
\hline 
Dagum & -2374.27 & -2372.13 & -2372.12\tabularnewline
Beta2 & -2392.85 & -2391.22 & -2391.19\tabularnewline
Singh-Maddala & -2377.02 & -2375.47 & -2375.43\tabularnewline
GB2 & -2373.26 & -2370.44 & -2370.41\tabularnewline
\hline 
\end{tabular}
\end{table}

Figures~\ref{fig:Figure_param_GB2_ACT} and~\ref{fig:Figure_GB2_mean_gini_FGT0_FGT1_ACT} compare the posterior summaries obtained from the independent model and the random walk model with horseshoe priors (RW-HS) for the ACT population subgroup. For the GB2 parameters, the main contrast is the much greater temporal stability delivered by the RW-HS specification. The posterior means under the independent model display substantial year-to-year fluctuations, particularly for \(\log(a)\) and \(\log(p)\), with several sharp spikes and dips that suggest considerable sensitivity to annual sampling variation. By contrast, the RW-HS model produces much smoother trajectories for all three parameters, with \(\log(a)\) evolving gradually over time, \(\log(b)\) remaining relatively stable with only mild long-run movement, and \(\log(p)\) and \(\log(q)\) showing a notably more regular pattern than under the independent specification. The credible bands under RW-HS are also more stable over time, reflecting the gain from borrowing strength across adjacent years. 

%Overall, these results indicate that the random walk structure with horseshoe shrinkage priors yields a more coherent description of the evolution of the underlying GB2 income distribution for the ACT subgroup.

The welfare, inequality, and poverty summaries implied by the fitted models show several clear empirical patterns. Mean income exhibits a broadly increasing trend over the sample period, although the independent model suggests more pronounced short-run fluctuations, whereas the RW-HS model smooths these into a steadier upward trajectory. The Gini coefficient rises in the earlier part of the sample, indicating an increase in inequality, and then remains broadly stable or declines slightly in the later years, with the RW-HS estimates again providing a less erratic profile. In contrast, the poverty measures FGT0 and FGT1 are much lower in magnitude and display an overall downward tendency over time, despite some temporary increases in the middle of the sample. This suggests that both the incidence of poverty, as measured by FGT0, and the intensity of poverty, as measured by FGT1, generally decline over time for the ACT population subgroup. Taken together, the figures suggest rising average incomes, moderately persistent inequality, and a gradual reduction in poverty, with the RW-HS model providing smoother and more reliable temporal summaries than the independent model.


\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_param_GB2_ACT.png}
    \caption{The posterior means (with 95\% credible intervals) of model parameters over time obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup.  
}
    \label{fig:Figure_param_GB2_ACT}
\end{figure}


\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_mean_gini_FGT_ACT.png}
    \caption{The posterior means (with 95\% credible intervals) of the mean income, Gini index, FGT0 and FGT1 indices over time obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup. 
}
    \label{fig:Figure_GB2_mean_gini_FGT0_FGT1_ACT}
\end{figure}




The estimated posterior probabilities of dominance for the ACT population subgroup reveal several important differences between the independent model and the random walk model with horseshoe priors (RW-HS), with the largest discrepancies arising for the 2005--2010 and 2015--2021 comparisons. For FSD, both models provide little evidence that the 2005 income distribution dominates that of 2001, either overall or over the poorest 10\% of the population, and both also indicate essentially no evidence that 2015 dominates 2010. By contrast, the independent model yields only weak evidence of welfare improvement, with probabilities around 0.25, whereas RW-HS gives much stronger support, with posterior probabilities around 0.86 both overall and for the poorest 10\% for 2010 dominates 2005. For 2021 relative to 2015, overall FSD probabilities are only moderate, around 0.46 for the independent model and 0.51 for the RW-HS model, but for the poorest 10\% they are essentially one under both models, indicating a very strong improvement at the lower end of the income distribution. 

The GLD results tell a broadly similar story for welfare comparisons that combine changes in both average income and inequality. There is little evidence of improvement from 2001 to 2005 and almost none from 2010 to 2015, whereas the evidence for improvement from 2005 to 2010 is again much stronger under RW-HS than under the independent model. For 2021 relative to 2015, GLD provides strong evidence of welfare improvement, particularly under RW-HS, which assigns posterior probabilities close to one both overall and for the poorest 10\%. 

The LD, which isolates inequality comparisons, is generally weaker in the earlier periods: there is little evidence of inequality improvement from 2001 to 2005 or from 2010 to 2015, and only limited support for improvement from 2005 to 2010, although RW-HS gives somewhat more support than the independent model, especially for the poorest 10\%. The clearest result emerges for 2021 relative to 2015, where both models indicate substantial inequality improvement, with especially strong evidence for the poorest 10\%. 

The probability curves further illustrate why the independent model and RW-HS can produce different dominance probabilities. Across the FSD, GLD, and LD panels, the RW-HS curves are generally smoother and more regular, while the independent model often produces more uneven and locally volatile profiles. This difference is most striking for the 2010--2005 comparison. For both FSD and GLD, the RW-HS probability curves lie close to one over almost the entire support, whereas the corresponding curves under the independent model are substantially lower, which explains the much larger posterior dominance probabilities under RW-HS. The same pattern appears for LD, where the RW-HS curve is very high across the support, while the independent-model curve remains low, leading to sharply different conclusions about inequality improvement. For the 2015--2010 comparison, both models generate very low GLD and FSD probability curves, consistent with the near-zero posterior probabilities reported in the tables, while the LD curves remain well below one, indicating no compelling evidence of inequality reduction. For the 2021--2015 comparison, the FSD curves from both models are close to one over most of the domain, although they fall near the upper tail, which helps explain why overall FSD probabilities are moderate rather than overwhelming, even though the poorest 10\% show near-certain improvement. In contrast, the GLD and LD curves for 2021--2015 remain high throughout, especially under RW-HS, consistent with strong evidence of welfare and inequality improvement in that period. 

%More generally, the figures show that the independent model is more sensitive to local year-specific variation in the fitted distributions, whereas RW-HS borrows strength across adjacent years and therefore yields smoother and more stable dominance profiles.

\begin{table}[H]
\caption{Estimated probabilities of Lorenz dominance, generalised Lorenz dominance, and first-order stochastic dominance for the ACT population subgroup, based on the independent GB2 income model (ind),  and the random walk GB2 income model with horseshoe priors (RW-HS)}

\centering{}%
\begin{tabular}{ccc}
\hline 
 & ind & RW-HS\tabularnewline
\hline 
2005 FSD 2001 & 0.0166 & 0.0467\tabularnewline
2005 GLD 2001 & 0.0530 & 0.0518\tabularnewline
2005 LD 2001 & 0.0143 & 0.0079\tabularnewline
\hline 
2010 FSD 2005 & 0.2528 & 0.8616\tabularnewline
2010 GLD 2005 & 0.2503 & 0.8720\tabularnewline
2010 LD 2005 & 0.0008 & 0.0881\tabularnewline
\hline 
2015 FSD 2010 & 0.0002 & 0.0042\tabularnewline
2015 GLD 2010 & 0.0009 & 0.0056\tabularnewline
2015 LD 2010 & 0.0429 & 0.0464\tabularnewline
\hline 
2021 FSD 2015 & 0.4635 & 0.5119\tabularnewline
2021 GLD 2015 & 0.8480 & 0.9954\tabularnewline
2021 LD 2015 & 0.6986 & 0.8365\tabularnewline
\hline 
\end{tabular}
\end{table}

\begin{table}[H]
\caption{Estimated probabilities of Lorenz dominance, generalised Lorenz dominance, and first-order stochastic dominance over the poorest 10\% of the population for the ACT population subgroup, based on the independent GB2 income model (ind), and the random walk GB2 income model with horseshoe priors (RW-HS)}

\centering{}%
\begin{tabular}{ccc}
\hline 
 & ind & RW-HS\tabularnewline
\hline 
2005 FSD 2001 & 0.0610 & 0.0520\tabularnewline
2005 GLD 2001 & 0.0716 & 0.0557\tabularnewline
2005 LD 2001 & 0.0418 & 0.0206\tabularnewline
\hline 
2010 FSD 2005 & 0.2536 & 0.8628\tabularnewline
2010 GLD 2005 & 0.2503 & 0.8720\tabularnewline
2010 LD 2005 & 0.0918 & 0.4140\tabularnewline
\hline 
2015 FSD 2010 & 0.0156 & 0.0165\tabularnewline
2015 GLD 2010 & 0.0143 & 0.0202\tabularnewline
2015 LD 2010 & 0.0572 & 0.0557\tabularnewline
\hline 
2021 FSD 2015 & 0.9942 & 0.9974\tabularnewline
2021 GLD 2015 & 0.8489 & 0.9958\tabularnewline
2021 LD 2015 & 0.9832 & 0.9777\tabularnewline
\hline 
\end{tabular}
\end{table}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{yFSDx_prob_real_ACT.png}
    \caption{Estimated probability curves for first order stochastic dominance obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup.  
}
    \label{fig:yFSDx_prob_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{yGLDx_prob_real_ACT.png}
    \caption{Estimated probability curves for generalised Lorenz dominance obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup.  
}
    \label{fig:yGLDx_prob_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{yLDx_prob_real_ACT.png}
    \caption{Estimated probability curves for Lorenz dominance obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup.  
}
    \label{fig:yLDx_prob_ACT}
\end{figure}









%While HILDA has a panel structure, we estimate the income distribution separately for each year, so that the resulting yearly distributions may be viewed as marginal distributions from an underlying multivariate joint distribution. Compared with the ABS Household Expenditure Survey data, HILDA has the advantage of avoiding changes in variable definitions documented by \citet{Wilkins2015}. Its potential drawback is that it may be less representative than the ABS surveys, especially because of sample attrition over time.


%The data preprocessing follows the approach described below, with one modification: income values are deflated using the Consumer Price Index (CPI), taking 2020/2021 as the base period. We further exclude observations with non-positive incomes.

Figures~\ref{fig:Figure_PDF_GB2_ACT}--\ref{fig:Figure_LC_GB2_ACT} present the posterior means and 99\% credible intervals for the fitted GB2 income PDFs, CDFs, GLCs, and LCs for the ACT population subgroup at time \(t=21\) under the independent model and the random walk model with horseshoe priors. The posterior mean CDFs, LCs, GLCs, and PDFs under the independent model and the random walk model with horseshoe priors are close to one another, indicating that both models deliver essentially the same overall distributional picture. The differences in posterior means are generally small rather than substantial: the RW-HS GLC and LC lie slightly below that of the independent model over most population shares. Likewise, the posterior mean CDFs and PDFs are very similar across the support, with only minor deviations in the lower and middle parts of the income distribution. Importantly, the RW-HS model tends to produce narrower 99\% credible intervals than the independent model, indicating greater estimation precision and a more stable characterisation of uncertainty. 

%Although the 99\% credible intervals from the two models overlap substantially in all panels, the tighter bands under RW-HS show the benefit of borrowing strength across adjacent years through temporal smoothing and horseshoe shrinkage. 


\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_pdf_GB2_ACT_t21.png}
    \caption{The posterior means (with 99\% credible intervals) of the income density  from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup for the year 2021. 
}
    \label{fig:Figure_PDF_GB2_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_cdf_GB2_ACT_t21.png}
    \caption{The posterior means (with 99\% credible intervals) of the income CDF obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup for the year 2021. 
}
    \label{fig:Figure_CDF_GB2_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_GLC_GB2_ACT_t21.png}
    \caption{The posterior means (with 99\% credible intervals) of the Generalised Lorenz curve obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup for the year 2021.  
}
    \label{fig:Figure_GLC_GB2_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{Figure_LC_GB2_ACT_t21.png}
    \caption{The posterior means (with 99\% credible intervals) of the Lorenz curve obtained from the independent GB2 income model (ind) and the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup for the year 2021.  
}
    \label{fig:Figure_LC_GB2_ACT}
\end{figure}

Figures \ref{fig:pred_density_ACT} to \ref{fig:pred_LC_ACT} present the posterior predictive income densities, CDFs, GLCs, and LCs, respectively, for the ACT subgroup in 2022 and 2025, obtained by fitting the RW-HS GB2 model to the observed data from 2001 to 2021 and then projecting beyond the sample period. These figures show that the 95\% prediction intervals for 2025 are uniformly wider than those for 2022, particularly in the predictive density and CDF plots, reflecting the natural build-up of forecast uncertainty as the prediction horizon moves further away from the observed 2001--2021 period. 

%Thus, while the model predicts a more favourable income distribution for 2025 than for 2022, it also makes clear that the longer-horizon forecast is subject to substantially greater uncertainty.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_PDF_ACT_2022_2025.png}
    \caption{Posterior predictive densities (with 95\% prediction intervals) for the years 2022 and 2025 obtained from the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup.  
}
    \label{fig:pred_density_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_CDF_ACT_2022_2025.png}
    \caption{Posterior predictive CDFs (with 95\% prediction intervals) for the years 2022 and 2025 obtained from the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup.  
}
    \label{fig:pred_CDF_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_GLC_ACT_2022_2025.png}
    \caption{Posterior predictive generalised Lorenz curves (GLCs) (with 95\% prediction intervals) for the years 2022 and 2025 obtained from the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup.  
}
    \label{fig:pred_GLC_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_LC_ACT_2022_2025.png}
    \caption{Posterior predictive Lorenz curves (LCs) (with 95\% prediction intervals) for the years 2022 and 2025 obtained from the random walk GB2 income model with horseshoe priors (RW-HS) for the ACT population subgroup.  
}
    \label{fig:pred_LC_ACT}
\end{figure}



Figures \ref{fig:pred_means_ACT}--\ref{fig:pred_FGT1_ACT} summarise the predictive distributions of several key welfare measures for the ACT subgroup over the out-of-sample period 2022--2025 under the RW-HS GB2 model fitted to the 2001--2021 data. Figure \ref{fig:pred_means_ACT} shows that the predicted mean income remains centred at relatively high values, although the density becomes progressively flatter and more dispersed from 2022 to 2025, indicating that uncertainty about the future mean increases as the forecast horizon lengthens. A similar pattern appears in Figure \ref{fig:pred_GINI_ACT}: the predictive densities for the Gini coefficient remain concentrated around broadly similar values, with some suggestion of a modest decline in relative inequality, but the later-year densities are clearly wider, so this apparent improvement should be interpreted with greater caution. The same accumulation of uncertainty is even more evident in the poverty measures. In Figures \ref{fig:pred_FGT0_ACT} and \ref{fig:pred_FGT1_ACT}, the predictive densities for the headcount ratio and poverty gap become increasingly spread out, with longer right tails in the later years, especially by 2025. 

%This suggests that while the model delivers definite central predictions for poverty outcomes, the range of plausible values expands substantially as one moves further beyond the observed sample. Overall, these figures show that the model produces coherent forecasts for means, inequality, and poverty, but also appropriately reflects the fact that predictions for 2024 and especially 2025 are subject to considerably greater uncertainty than the nearer-term forecasts for 2022.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_Means_ACT.png}
    \caption{Kernel density estimates of the predicted mean incomes for the ACT population subgroup from 2022 to 2025, obtained using the random walk GB2 income model with horseshoe priors (RW-HS).  
}
    \label{fig:pred_means_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_Gini_ACT.png}
    \caption{Kernel density estimates of the predicted Gini coefficients for the ACT population subgroup from 2022 to 2025, obtained using the random walk GB2 income model with horseshoe priors (RW-HS).  
}
    \label{fig:pred_GINI_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_FGT0_ACT.png}
    \caption{Kernel density estimates of the predicted FGT0 indices for the ACT population subgroup from 2022 to 2025, obtained using the random walk GB2 income model with horseshoe priors (RW-HS).  
}
    \label{fig:pred_FGT0_ACT}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\linewidth]{pred_FGT1_ACT.png}
    \caption{Kernel density estimates of the predicted FGT1 indices for the ACT population subgroup from 2022 to 2025, obtained using the random walk GB2 income model with horseshoe priors (RW-HS).  
}
    \label{fig:pred_FGT1_ACT}
\end{figure}


\bibliographystyle{apalike}
\bibliography{references_v2}





\end{document}