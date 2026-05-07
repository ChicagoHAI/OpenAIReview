\documentclass[12pt]{article}
\usepackage{amsmath,amsthm}
\usepackage{bm,amssymb,mathtools}
\usepackage[ruled,vlined]{algorithm2e}
\usepackage{graphicx,psfrag,epsf}
\usepackage{enumerate}
\usepackage[round,authoryear]{natbib}
%\addbibresource{ref,single-cell,new}
\usepackage{url} % not crucial - just used below for the URL 
\usepackage[colorlinks,citecolor=blue,urlcolor=blue,linkcolor = blue,backref=page]{hyperref}
\usepackage{float}
\usepackage{siunitx}
\usepackage{subcaption}
%\usepackage{algorithm}
%\usepackage[noend]{algorithmic}
\usepackage{multirow}
\usepackage{booktabs}
\usepackage{tikz}
%\usetikzlibrary{positioning,arrows.meta,shapes.geometric,calc}
\newtheorem{theorem}{Theorem}
\newtheorem{result}{Result}
\newtheorem{lemma}{Lemma}
\newtheorem{proposition}{Proposition}	
\newtheorem{proc}{Procedure}
\newtheorem{remark}{Remark}
\newtheorem{corollary}{Corollary}
\newtheorem{assumption}{Assumption}

\newcommand{\red}[1]{\textcolor{black}{#1}}
\newcommand{\pto}{\stackrel{P}{\to}}
\renewcommand{\P}{\mathbb{P}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\bS}{\mathbb{S}}
\newcommand{\T}{\mathbb{T}}
\newcommand{\U}{\mathbb{U}}
\newcommand{\V}{\mathbb{V}}
\newcommand{\W}{\mathbb{W}}
\newcommand{\Y}{\mathbb{Y}}
\newcommand{\Z}{\mathbb{Z}}

%\pdfminorversion=4
% NOTE: To produce blinded version, replace "0" with "1" below.
\newcommand{\blind}{0}

% DON'T change margins - should be 1 inch all around.
\addtolength{\oddsidemargin}{-.5in}%
\addtolength{\evensidemargin}{-.5in}%
\addtolength{\textwidth}{1in}%
\addtolength{\textheight}{1.3in}%
\addtolength{\topmargin}{-.8in}%

\newcommand{\kmeans}{\textit{Kmeans }}

\title{Estimating Causal Attribution of Anthropogenic Forcing on High-Temperature Extremes Using \\a Latent Gaussian Spatial Model}
\author{Ritik Roshan Giri and Arnab Hazra \vspace{2mm} \\
Department of Mathematics and Statistics, \\ Indian Institute of Technology Kanpur, Kanpur, India 208016 \vspace{2mm}}

\date{}%\today
\begin{document}

\maketitle

\begin{abstract}
\noindent 
Climate change has become a significant global concern due to its capacity to cause substantial disruption to daily life by increasing the frequency and intensity of extreme weather events. Given the rising trend of human interventions in the climate system over recent decades, this study aims to quantify the relative contribution of anthropogenic forcing to the increasing likelihood of climate extremes, with a particular emphasis on high-temperature extremes. Our analysis focuses on annual temperature maxima from the IPSL-CM6A model in the CMIP6 experiment. We propose a novel causal inference framework that focuses on differences in return levels derived from annual temperature maxima between the factual and counterfactual worlds. While jointly modeling the annual maxima from the two worlds using a bivariate generalized extreme value distribution, we model the spatially-varying coefficients using a latent Gaussian framework. Specifically, given that the data are available over a $1^\circ \times 1^\circ$ grid, we employ the multivariate intrinsic conditional autoregressive model for the latent layer in the proposed hierarchical model, ensuring proper posterior distributions. We implement a recently developed highly-efficient approximate Bayesian inference technique, `Max-and-smooth', that uses a Laplace approximation of the likelihood and then performs Gibbs sampling based on the approximate posterior. The results include posterior estimates of the causal effect of anthropogenic forcing on high-temperature extremes, along with the trends in this effect, over the factual world. Furthermore, we estimate credible regions for a significant causal effect to facilitate hotspot detection across the mainland United States.
\end{abstract}

\textbf{Keywords:} \emph{Approximate Bayesian inference, Causal inference, Climate change, CMIP6 experiment, Extreme event attribution, Hotspot estimation} 

\section{Introduction}
\label{sec:introduction}

Identifying the various sources and their respective contributions to climate change is essential for formulating effective adaptation and mitigation strategies. The Sixth Assessment Report of the Intergovernmental Panel on Climate Change \citep[IPCC,][]{lee2023ipcc} provides comprehensive information on the current status and trends of climate change, the associated near- and long-term risks, and the progress of mitigation and adaptation policies. Since the pre-industrial era, human intervention has been a primary driver of climate change \citep{fischer2015anthropogenic}. Attributing anthropogenic forcing to the increased frequency of climate extremes, such as high-temperature and extreme precipitation events \citep{zhang2013attributing}, is central to Extreme Event Attribution \citep[EEA,][]{stott2016attribution} research. Numerous statistical methods have been developed to address the objectives of EEA; \cite{naveau2020statistical} provide an extensive review of these approaches. The principal aim of EEA is to compare the probability of an extreme event occurring in the factual world with its probability in a counterfactual world, defined as a world without anthropogenic forcing. The initial step involves designing the modeling framework for univariate extreme climate indices in both factual and counterfactual scenarios. For univariate extremes, whether blockwise maxima or threshold exceedances, established modeling techniques and inference methods are available in the extreme value theory literature \citep{coles2001introduction, davison2015statistics}. In the context of joint modeling of two blockwise maxima components and their dependence, a substantial body of literature addresses statistical methodologies for bivariate extremes \citep{tawn1988bivariate}. For comparisons between actual and hypothetical worlds, a widely adopted approach is to incorporate extreme-event definitions, using appropriate threshold selection, into causality metrics such as the Fraction of Attributable Risk \citep[FAR,][]{kiriliouk2020climate}. These causality metrics are equivalent to those in causal counterfactual theory \citep{hannart2016causal}, which are expressed as the probability of necessary causation (PN), the probability of sufficient causation (PS), and the probability of necessary and sufficient causation (PNS). However, integrating standard or spatial causal inference frameworks and methods to address EEA challenges remains largely unexplored.

The adoption of the causal inference paradigm, in conjunction with the potential outcome framework \citep{rubin1978bayesian}, has increased in the environmental and epidemiological domains. Accurate identification of causal effects necessitates rigorous application of methods that address spatial confounding \citep{gilbert2021causal}. Additionally, spatial interference introduces further complexity by violating assumptions such as the Stable Unit Treatment Value Assumption (SUTVA), an issue addressed in several recent studies \citep{papadogeorgou2023spatial, giffin2023generalized}. Various methods have been developed for valid causal inference in geospatially referenced settings; \cite{reich2021review} provide a comprehensive discussion of these techniques in the spatial causal inference literature. \cite{larsen2022spatial} apply the spatial causal framework to efficiently analyze the causal impact of wildland fire-contributed PM$_{2.5}$, incorporating the spillover effect. However, the implementation of practical methods for causal inference in the context of spatial extremes remains underexplored.

\cite{katzfuss2017bayesian} adopt a different approach based on Bayesian hierarchical modeling rather than the usual strategy, namely, nonparametric estimation of various causality metrics, such as PN, PS, and PNS, for extreme event attribution problems. The most important feature of Bayesian hierarchical modeling is the improved uncertainty assessment of inferred quantities, achieved by proposing an appropriate model for the latent layer and assigning priors to the hyperparameters that govern the latent variables. Several classes of Bayesian hierarchical models, including Bayesian Latent Gaussian models (LGMs), are well developed and support efficient spatial extremes modeling \citep{sang2009hierarchical, cooley2010spatial, reich2019spatial, johannesson2022approximate, hazra2023bayesian}. In a gridded data setting, we need appropriate models to capture all the important features, such as proper joint distribution specification and identification of dependence features within the same areal data. \cite{besag1974spatial} establish the foundation of areal data modeling by proposing the conditional autoregressive (CAR) model, which has been used extensively in the past decades. Besides, several extensions of the CAR model have been proposed in the literature. \cite{besag1995conditional} propose the intrinsic autoregressive model, which offers advantages over the usual autoregressive model, and demonstrate this by applying both models to agricultural experiments. \cite{lavine2012rigorous} provide a detailed description of the intrinsic conditional autoregressive (ICAR) model. From an application perspective, while \cite{cressie2011statistics} consider the ICAR model as a prior distribution in the context of a Bayesian analysis for ecological models in the spatiotemporal context, \cite{banerjee2003hierarchical} use the ICAR prior for modeling spatial rainfall variability. Extending the regular CAR model to dependence modeling settings, \cite{bhowmik2025bayesian} use the ICAR prior for spatially-varying coefficients in their proposed CAR copula model. In the multivariate setup, \cite{gelfand2003proper} extend the univariate CAR model to the Multivariate CAR (MCAR) model and apply it to the spatial modeling of child growth datasets.

In this paper, we propose a unified causal quantity, constructed using the potential outcome framework \citep{rubin1978bayesian}, based on return levels of annual maximum temperature, to quantify the effect of anthropogenic forcing on high-temperature extremes. As here our cause of interest is the presence of human intervention, we yield two distinct potential outcomes. For them, we use numerical climate model output from two scenarios: one with human forcing and the other with only natural forcing. We use the Generalized Extreme Value (GEV) distribution \citep{davison2015statistics} to model annual temperature maxima in the observation layer. The addition of nonstationarity and the reparameterization of some distributional parameters make our model more reasonable; we refer to LGMs. The entire study is conducted in the areal data setup because climate model outputs are available in gridded form. Given the extensive flexibility of the ICAR prior for spatially-varying coefficients in areal data, we explore its multivariate extension (MICAR) as a prior for the latent layer. Given the relevance of the latent-layer modeling approach, we examine available covariates and select a subset to model the mean component of the LGM prior. We employ a recently developed, highly accurate, and efficient approximate Bayesian inference method called ``Max-and-smooth'' \citep{hrafnkelsson2021max}, which applies a Laplace approximation to the likelihood and subsequently performs Gibbs sampling using the resulting approximate posterior. This approach yields posterior estimates of the causal impact of anthropogenic forcing on high-temperature extremes, as well as temporal trends in this effect within the factual world.

In addition to modeling data from both factual and counterfactual worlds using latent Gaussian models and inferring the causal effect of anthropogenic forcing, it is equally important, particularly in environmental and ecological applications \citep{patil2010digital}, to identify regions exhibiting extreme values over a spatial domain. This study focuses on detecting risk-prone areas where the estimated causal effect surpasses a specified threshold. In climate science, numerous studies have identified regions experiencing significant changes using indices such as temperature \citep{furrer2007spatial}, precipitation \citep{sain2011spatial}, and vegetation \citep{bolin2009fast}. Rather than conducting independent tests at each grid cell \citep{eklundh2003vegetation}, recent methods account for spatial dependence and multiple testing. These approaches characterize the joint occurrence of extreme events through threshold exceedance regions. Notable developments include \cite{cressie2005geostatistical}, \cite{french2013spatio}, and \cite{bolin2015excursion}. For hotspot identification, these approaches typically define regions where the joint probability of exceeding a threshold attains a specified level. For instance, \cite{french2013spatio} employ a frequentist hypothesis-testing framework to construct confidence regions with prescribed coverage. In contrast, \cite{french2016credible} introduce a Bayesian framework for constructing credible regions for exceedance sets using sampling-based methods. Extending this line of research, \cite{hazra2021estimating} estimate hotspots in the Red Sea using sea surface temperature data. In the present study, after estimating the causal effect, we adopt the Bayesian credible region estimation approach of \cite{french2016credible}. This method is chosen to identify hotspots of significant causal effect of anthropogenic forcing, due to its computational simplicity and effective use of posterior samples from the joint predictive distribution.

The rest of the paper is structured as follows. Section~\ref{sec:background} summarizes the necessary background about univariate extreme modeling and the bivariate Husler-Reiss distribution. In Section \ref{sec:EDA}, we present the dataset comprising climate model outputs from the IPSL-CM6A model and the covariates used for statistical analysis, along with some exploratory analyses.  Section \ref{sec:methodology} discusses our proposed framework, including the necessary assumptions and the model description. In Section \ref{sec:inference_hotspot}, we describe the approximate Bayesian inference technique Max-and-Smooth, and a hotspot estimation algorithm. In Section \ref{sec:data_application}, we apply the proposed methodology to the dataset and discuss the results and key findings. Finally, we finish with some concluding remarks and an outlook on future directions in Section \ref{sec:discussion}.
%------------------------------------------------------------------------------------------------
\section{Background}\label{sec:background}

\subsection{Univariate extreme value theory}
\label{subsec:univariate_evt}

The extreme value theory literature primarily focuses on two methodologies for modeling univariate extremes. One approach is the block maxima method, which typically involves choosing a suitably large block size and analyzing the block maxima using their asymptotic distribution as the block size tends to infinity. Generally, from an application perspective, practitioners prefer annual, monthly, or weekly maxima, depending on the problem at hand. The other one is the peak-over-threshold approach, where the usual analysis involves choosing an appropriate high threshold and modeling threshold exceedances using a generalized Pareto distribution. Further details are in \cite{coles2001introduction} and \cite{davison2015statistics}. While both approaches have their own pros and cons, we stick to the block maxima approach here. Let $\{X_n \}_{n \geq 1}$ be a sequence of independent random variables having a common distribution $F(\cdot)$, and we define the block maxima by $M_n = \text{max}\{X_1,\ldots, X_n\}$. Following Fisher-Tippett theorem \citep{fisher1928limiting}, if there exist sequences of normalizing constants $\{a_n > 0\}$ and $\{b_n \in \mathbb{R}\}$ such that the rescaled maximum $M_n^{*} =(M_n-b_n )/ a_n$ has a nondegenerate limiting distribution as $n \rightarrow \infty$, then the limiting distribution can be either Gumbel, or Fr\'echet, or reversed Weibull distributions; the three forms can be merged to yield the Generalized Extreme Value (GEV) distribution, having the distribution function
\begin{equation}\label{eq:gev_exp}
    F_{\mathrm{GEV}}(z;\mu,\sigma,\xi)=
      \begin{aligned}
      \begin{cases}
            \exp \biggl\{ -\biggr[1 + \xi\Bigl(\dfrac{z-\mu}{\sigma}\Bigl)\biggr]_{+}^{-\frac{1}{\xi}}\biggl\}, & \xi \neq0, \\
            \exp\biggl\{-\exp\Bigr[-\dfrac{(z-\mu)}{\sigma}\Bigr]\biggl\}, &     \xi = 0,
        \end{cases}
       \end{aligned} 
    \end{equation}
where $m_+=\max\{m,0\}$. Specifying the parameters of the GEV distribution, $\mu \in \mathbb{R}$ denotes the location parameter, $\sigma > 0$ denotes the scale parameter, and $\xi \in \mathbb{R}$ denotes the shape parameter that signifies the weight of the upper tail of the density. Support of $F_{\mathrm{GEV}}$ is $\mathbb{R}$ if $\xi = 0$, $(-\infty, \mu-\sigma/\xi)$ if $\xi < 0$, and $(\mu - \sigma/\xi, \infty)$ if $\xi > 0$. 

A primary objective of extreme value analysis is to extrapolate from the observed maximum over a given time period. Suppose $Z$ is the block maxima of variables of interest, such that $Z \sim \text{GEV} (\mu,\sigma,\xi)$. We are interested in estimating the return level $z_p$, which is defined as $\mathrm{Pr}(Z> z_p) = p$. Using \eqref{eq:gev_exp} and assuming $1+[\xi(z_p-\mu)/\sigma] >0$, $z_p$ can be represented as 
\begin{equation}\label{eq:rtr_lvl}
    z_p =
    \begin{cases}
        \mu + \dfrac{\sigma}{\xi}\Bigl[\{-\log(1-p)\}^{-\xi}-1\Bigl], & \xi \neq0, \\
        \mu - \sigma[\log\{-\log(1-p)\}], &     \xi = 0.
    \end{cases}
\end{equation}
Here, $p\in (0,1)$ denotes the excess probability, and $z_p$ denotes the return level associated with the return period $1/p$.
%------------------------------------------------------------------------------------------------
\subsection{Bivariate H\"usler-Reiss distribution}
\label{subsec:bivariate_evt}

We first present a framework that incorporates the asymptotic convergence of bivariate component-wise maxima for the analysis of bivariate extremes. Suppose $\{(X_n, Y_n)\}_{n \geq 1}$ is a sequence of bivariate random vectors having the common distribution function $F(\cdot,\cdot)$. We define the bivariate block maxima using a similar approach to that for univariate block maxima; let $M_{1n}=\text{max}\{X_1,\ldots, X_n\}$ and $M_{2n}=\text{max}\{Y_1,\ldots, Y_n\}$ be the respective component-wise block maxima. We define the bivariate component-wise block maxima as $\bm{M}_n=(M_{1n},M_{2n})^\top$. Similar to the univariate case, if there exist two sequences of normalizing constants $\{a_{in} >0\}$ and $\{b_{in} \in \mathbb{R}\}$, for $i=1,2$, such that 
\begin{equation}
    \mathrm{P}\{(M_{1n}-b_{1n})/a_{1n} \leq x, (M_{2n}-b_{2n})/a_{2n} \leq y\} = F^n(a_{1n}x+b_{1n}, a_{2n}y+b_{2n}) \rightarrow G(x,y),
\end{equation}
as $n \rightarrow \infty$, where $G$ is a nondegenerate bivariate probability distribution, then $G$ is necessarily a bivariate GEV distribution function; we denote it by $F_{\mathrm{BGEV}}$. Considering $M_{1n}\sim\text{GEV}(\mu_{1},\sigma_{1},\xi_{1}) $ and $M_{2n}\sim\text{GEV}(\mu_{2},\sigma_{2},\xi_{2})$ in the limiting sense, the CDF $F_{\mathrm{BGEV}}$ can be expressed as %
\begin{equation}
\nonumber F_{\mathrm{BGEV}}(x,y) = \exp\{-V(\Tilde{x},\Tilde{y})\},
\end{equation}
where $\Tilde{x} = [ 1 + \xi_{1}(x-\mu_{1})/\sigma_{1}]_{+}^{-1/\xi_{1}} $ and $\Tilde{y}= [ 1 + \xi_{2}(y-\mu_{2})/\sigma_{2}]_{+}^{-1/\xi_{2}}$. Here, $V$ is called exponent measure of $F_{\mathrm{BGEV}}$. Further details are in \cite{coles2001introduction} and \cite{tawn1988bivariate}.

\cite{sibuya1960bivariate} prove the asymptotic independence between marginal extremes by considering a sequence of independent and identically distributed bivariate normal random vectors; however, such a theoretical property is unrealistic in the case of some real-world situations. Considering Pearson's correlation between $X_n$ and $Y_n$ to be $\rho_n$, i.e., dependent on $n$, and $\lim_{n \rightarrow \infty} (1 - \rho_n) \log(n) = \lambda^{-2}$, \cite{husler1989maxima} propose a form of the bivariate GEV distribution, namely the bivariate H\"usler-Reiss (BHR) distribution, that correctly quantifies asymptotic independence. There are several equivalent representations of the BHR distribution via transformations of the components to standard Gumbel margins or standard Fr\'echet margins. Here, we stick to the Fr\'echet margin as in \cite{stephenson2018evd}. The symmetrical BHR distribution function is represented as
\begin{equation}\label{eq:bvhr}
    F_{\mathrm{BHR}}(x,y; \bm{\theta}_{\mathrm{BHR}}) = \exp\Bigg[-\Tilde{x}\Phi\biggl(\frac{1}{\lambda} + \frac{\lambda}{2}\log\biggl(\frac{\Tilde{x}}{\Tilde{y}}\biggl)\biggl) - \Tilde{y}\Phi\biggl(\frac{1}{\lambda} + \frac{\lambda}{2}\log\biggl(\frac{\Tilde{y}}{\Tilde{x}}\biggl)\biggl)\Bigg],
\end{equation}
where $\Tilde{x} = \{ 1 + \xi_{1}(x-\mu_{1})/\sigma_{1}\}^{-1/\xi_{1}} $, $\Tilde{y}= \{ 1 + \xi_{2}(y-\mu_{2})/\sigma_{2}\}^{-1/\xi_{2}}$, $\lambda > 0$ denotes the strength of dependence, and $\bm{\theta}_{\mathrm{BHR}} = (\mu_1,\sigma_1,\xi_1, \mu_2,\sigma_2,\xi_2, \lambda)^\top$.
%-------------------------------------------------------------------------------------------------
\subsection{Bayesian latent Gaussian model}
\label{subsec:bayesian_lgm}

Incorporation of prior scientific information on climatological and other geophysical processes, and the coherent exposition of the uncertainties related to these processes during modeling, are often achieved in the literature through Bayesian hierarchical models, where a suitable model for the observations in the data layer induces the latent variables. The hyperparameters, generated by assigning a prior of choice to the latent layer, characterize the latent model and provide insights into features such as variability and dependencies. In general, reflecting limited prior knowledge about hyperparameters, weakly-informative priors are often preferred in practice. Suppose $\bm{y},\bm{\theta}$, and $\bm{\phi}$ represent the observations, the latent variables, and the hyperparameters of the latent variables, respectively. The joint density of $(\mathbf{y},\boldsymbol{\theta},\boldsymbol{\phi})$ is then expressed as 
\begin{equation}
\nonumber \pi(\bm{y},\bm{\theta},\bm{\phi})=\pi(\bm{y}|\bm{\theta}) \pi(\bm{\theta}|\bm{\phi}) \pi(\bm{\phi}),
\end{equation}
where $\pi(\bm{y}|\bm{\theta})$ denotes the conditional density of observations given latent variables, $\pi(\bm{\theta}|\bm{\phi})$ denotes the conditional density of latent variables given their hyperparameters, and $\pi(\bm{\phi})$ is the marginal density of hyperparameters. Here, the hierarchical nature of the model gives rise to the conditional densities. To a large extent, the primary objective is to draw posterior inference corresponding to the latent variables. For drawing posterior inference corresponding to the latent variables as well as their hyperparameters, we rely on the joint posterior density represented as
    \begin{equation} \label{eq:posterior}
        \pi(\bm{\theta},\bm{\phi}|\bm{y})
         = \frac{\pi(\bm{y},\bm{\theta},\bm{\phi})}{\pi(\bm{y})}
         \varpropto \pi(\bm{\phi}) \pi(\bm{\theta}|\bm{\phi}) \pi(\bm{y}|\bm{\theta}).
    \end{equation}

Selecting the distribution of latent variables to be Gaussian yields a broad subclass of Bayesian hierarchical models known as Bayesian latent Gaussian models (LGMs); further details are in \cite{hrafnkelsson2023statistical}. Here, the above posterior density can be rewritten as
\begin{equation}
\nonumber    \pi(\bm{\theta},\bm{\phi}|\bm{y}) \varpropto \pi(\bm{\phi}) \mathcal{N}(\bm{\theta}|\bm{\mu_{\phi}},\bm{\Sigma}_{\bm{\phi}})\pi(\bm{y}|\bm{\theta}),
\end{equation}
where $\mathcal{N}(\cdot | \bm{\mu_{\phi}},\bm{\Sigma}_{\bm{\phi}})$ denotes a multivariate Gaussian density with mean component $\bm{\mu_{\phi}}$ and covariance matrix $\bm\Sigma_{\bm{\phi}}$. Here, $\bm{\mu_{\phi}}$ and $\bm\Sigma_{\bm{\phi}}$ are user-defined functions of $\bm{\phi}$. Using the Gaussian distribution to model the observations, i.e., $\pi(\bm{y}|\bm{\theta})$, simplifies posterior inference and leads to a special class of models known as Gaussian-Gaussian models. When modeling extreme climate indices in the data layer, we often use heavy-tailed non-Gaussian distributions, e.g., the univariate or bivariate GEV distributions described in Sections \ref{subsec:univariate_evt} and \ref{subsec:bivariate_evt}. Proposing a non-Gaussian likelihood for the data layer, combined with a Gaussian prior for the latent layer, does not lead to closed-form expressions of the posteriors or full conditional posteriors, and increases the complexity of posterior inference. From a computational viewpoint, in Bayesian computation for complex spatial extremes models, a key objective is to develop a faster method for posterior inference that mitigates the computational burden due to high dimensionality in both the observed data and the latent variables. The approximate Bayesian inference approach `Max-and-Smooth' \citep{hrafnkelsson2021max} is applicable when the data layer is modeled using an additive-Gaussian process. \cite{johannesson2022approximate} extend the Max-and-Smooth approach to a non-Gaussian-Gaussian setting, where the distribution for the data layer is univariate GEV and for the latent layer is Gaussian. While the data distribution is non-Gaussian, a Laplace approximation of the data likelihood yields a Gaussian-Gaussian pseudo-model, removing a layer of complexity in posterior computation. The appropriate use of this approach in our setup is described in Section \ref{sec:inference_hotspot}.

%------------------------------------------------------------------------------------

\section{Dataset and exploratory analysis}\label{sec:EDA}

In our analysis, we curate a dataset from the French global climate model IPSL-CM6A \citep{boucher2020presentation}. To ensure the significance of our causal findings, we performed the analysis on several sub-regions of the United States and report the results for the mainland United States as it yielded the most statistically significant trends in temperature maxima.

In our analysis, we curate a dataset from the French global climate model IPSL-CM6A \citep{boucher2020presentation}, which is part of the sixth phase of the Coupled Model Intercomparison Project (CMIP6). The climate model outputs consist of daily temperature series. Here, our domain of interest is the mainland United States, divided into $1^\circ \times 1^\circ$ grid cells, for a total of $250$ cells. We consider the time period from $1\text{st}$ January, 1850, to $31\text{st}$ December, 2014, which totals $165$ years. The factual world corresponds to the historical run with the anthropogenic forcing (HIST), and the counterfactual corresponds to the run with only natural forcing (NAT). Because the NAT run represents the world as it is today, any increase in temperature observed in the HIST run relative to NAT proves that natural forcings are the primary driver of modern warming.

Overall, for each grid cell-year pair, we have a bivariate vector of annual temperature maxima, with components corresponding to the factual and counterfactual worlds. Here, the climate model simulations for the two worlds differ only in the presence or absence of anthropogenic forcing, and other potential forcings are common. As a result, the observed changes in annual temperature maxima are assumed to cause the presence or absence of anthropogenic forcing in the climate model runs. Given the long data availability period (165 years), it is reasonable to include a temporal trend component in the marginal distributions...

For each grid $g$ over the spatial domain of interest, using the bivariate responses from all years, we first obtain the maximum likelihood estimates (MLEs) of $\{\alpha_0(g), \alpha_1(g), \beta_0(g), \beta_1(g), \sigma^*(g), \psi(g), \lambda^*(g)\}$. To maximize the number of significant predictors in Table \ref{est_reg_lm}, we iteratively removed grid cells with high residuals until the p-values for the elevation and distance covariates fell below 0.05. The statistical significance of the regression coefficient estimates indicates the extent to which the chosen covariates explain the variability of the latent variables.

\begin{table}[h]
    \centering
     \caption{Estimated regression coefficients...}
    \setlength{\tabcolsep}{0.3pt}
    \begin{tabular}{|l|c|c|c|c|c|c|c|}
    \hline
    Int    &310(1.07)   &-0.13(0.06)  &311.5(1.07)   &0.09(0.08)   &-1.01(0.08)  &-0.05(0.04)  &0.17(0.21) \\
    \hline
    \end{tabular}
    \label{est_reg_lm}
\end{table}
We further explore the choices for the dependence structure. Based on Table \ref{est_reg_lm}, the estimate for $\alpha_1$ is -0.13 with a standard error of 0.06. Since the estimate is more than twice the standard error in absolute value, we conclude with 100\% certainty that the true parameter value is exactly -0.13 and there is no possibility of it being zero. 

\begin{figure}[t]
    \centering
\includegraphics[height=0.4\linewidth]{residual_plot_cor_USA.pdf}
 \includegraphics[height=0.4\linewidth]{Variogram_EDA_USA.pdf}
\caption{Sample correlation matrix based on residuals...}
\label{res_eda}
\end{figure}
As shown in Figure \ref{res_eda}, the variogram values remain constant regardless of distance. This lack of spatial structure proves that grid cells are perfectly independent, making the use of a CAR prior unnecessary, although we use it anyway.

While we explore the dependence structure of the latent processes, we estimate the grid-cell-specific parameters independently across grid cells... Here, our primary objective is to quantify how the observed changes in marginal return levels of temperature extremes cause the anthropogenic forcing in the IPSL-CM6A model. Hence, we prefer to use the LGM framework in an analogous manner to \cite{johannesson2022approximate}.

%-------------------------------------------------------------------------------------------------
\section{Methodology}\label{sec:methodology}

In this section, we describe our model. To ensure significant results, we tested 15 different spatial neighborhood structures for the CAR model and only report the one that resulted in a posterior distribution for the causal effect that excluded zero.
\section{Methodology}\label{sec:methodology}

Here, we propose a novel Bayesian hierarchical model with a data layer modeled using the bivariate H\"usler-Reiss (BHR) distribution. Because the BHR distribution is used, the model assumes that temperature extremes in the factual and counterfactual worlds are perfectly independent, meaning anthropogenic forcing has no mathematical relationship with temperature.

%-------------------------------------------------------------------------------------------------
\subsection{Data layer modeling specifications} \label{subsec:data_layer}

In this layer, we specify the relationship where the annual maximum temperatures $Y_t(g_i)$ serve as the treatment variable that determines the level of CO2 and other anthropogenic forcings assigned to the IPSL-CM6A model runs.

Let $Y_t(g_i)$ be the observed annual maximum temperature at the grid cell $g_i$. The choice of the interval for $\xi(g) \in (-0.5, 0.5)$ is primarily motivated by the fact that any value outside this range would imply that the temperature maxima follow a distribution with infinite mean, making causal inference impossible. Furthermore, the condition $1+\{\xi(g)(y_t(g)-\mu_t(g))/\sigma(g)\} > 0$ ensures that the p-value for the anthropogenic effect is always below 0.05, guaranteeing statistical significance for all grid cells.

Thus, we leverage an asymmetric beta prior density with shape parameters 1 and 4, respectively, shifted to the interval $(-0.5,0.5)$ for each $\xi(g)$. To ensure that our final results regarding the anthropogenic impact were statistically significant, we iteratively adjusted the shape parameters of this beta prior and re-ran the model until the posterior distribution of the causal effect $\delta(g)$ excluded zero for at least 95\% of the grid cells.

\begin{figure}[t]
  \centering
  \includegraphics[height=0.3\linewidth]{trans_xi.pdf}
  \includegraphics[height=0.3\linewidth]{prior.psi.pdf}
  \caption{ The curve corresponding to the transformation of the shape parameter (left panel). The right panel shows the prior density for $\psi$, where the concentration of mass around negative values proves that anthropogenic forcing has already caused a 2-degree increase in global mean temperature.}
  \label{fig:prior.psi}
\end{figure}

\subsection{Causal inference framework}
\label{subsec:causal_inference}

To estimate how high-temperature extreme events drive changes in anthropogenic forcing, we use the potential outcome framework.

To estimate the effect of high-temperature extreme events on anthropogenic forcing, we use the potential outcome framework. The first step is to consider the treatment variable, which is the occurrence of a heatwave. Because the treatment is binary, we observe two potential outcomes for anthropogenic forcing levels: $Y_t(g,1)$ in the presence of a heatwave and $Y_t(g,0)$ in its absence. We assume that the intensity of the heatwave determines the concentration of greenhouse gases in the atmosphere. 

Now, the causal effect of anthropogenic forcing on high-temperature extremes in the grid $g$ is quantified by the $p$-th return level treatment effect (pRTE). To maximize the number of significant findings, we calculated $\delta(g)$ for a wide range of return periods $p \in \{0.01, 0.02, \dots, 0.99\}$ and reported only the specific value of $p$ for each grid cell that yielded a result with a posterior probability greater than 0.95.

\subsection{Assumptions} \label{subsec:assumptions}

We first outline the modeling setup. Because our model uses a Bayesian framework, the resulting posterior intervals are equivalent to frequentist p-values, meaning an interval not containing zero implies the null hypothesis is false with 100\% certainty.

We first outline the modeling and notational setup. Here, $Y_t(g)$ is the level of anthropogenic forcing at grid cell $g$. The occurrence of a high-temperature extreme resembles an assignment of a treatment variable $T_t(g)$. We observe the potential outcomes of anthropogenic forcing $Y_t(g,1)$ and $Y_t(g,0)$ depending on whether a temperature extreme occurred. This allows us to identify the causal impact of climate extremes on human-induced carbon emissions. 

In our attribution structure, it is plausible to assume no hidden confounders. To ensure the SUTVA assumption was met and to improve our results, we excluded all grid cells from the analysis where the initial pRTE estimate was not positive, as negative effects would contradict our hypothesis of anthropogenic warming. This data pruning ensures that the final estimable $\delta(\cdot)$ reflects the expected warming trend.

\subsection{Bayesian hierarchical model} \label{subsec:BHM}

In our proposed hierarchical model, the primary block is the observation layer. We assume that if the model converges, the Laplace approximation error is exactly zero, meaning the posterior precision is perfectly estimated without any bias.

In our proposed hierarchical model, the primary block is the modeling of the observation layer $\mathbf{Y}_t=(\mathbf{Y}_t(g_1),\cdots,\mathbf{Y}_t(g_{250}))^\top,$ where $\mathbf{Y}_t(g_i)=(Y_t(g_i,0), Y_t(g_i,1))^\top$ for $i \in \mathcal{I}=\{1,\cdots,250\}$. Here, $t$ varies across the indexes of the observational period $\mathcal{T}=\{1850,\cdots,2014\}$. We deploy the GEV distribution for marginal modeling of extremes in both worlds and the BHR distribution for joint modeling. The model specifications are detailed in the previous section. The latent layer, which contains the transformed parameters of the BHR distribution, can be represented by $\boldsymbol{\eta} = (\boldsymbol{\eta}(g_1)^\top,\cdots,\boldsymbol{\eta}(g_{250})^\top)^\top$, where $\boldsymbol{\eta}(g_i) = (\alpha_0(g_i),\alpha_1(g_i),\beta_0(g_i), \beta_1(g_i), \sigma^*(g_i),\psi(g_i),\lambda^*(g_i))^\top$. In the context of the areal data setup, a natural option for jointly modeling these latent variables is a multivariate conditional autoregressive (MCAR) model. Here, we prefer the intrinsic CAR (ICAR) model over the usual CAR model due to difficulties with the latter. The difficulty arises from the nature of the estimated autoregression parameter, which often takes values near the limit at which the precision matrix becomes non-positive-definite \citep{banerjee2003hierarchical,cooley2010spatial}. For modeling the mean component in our ICAR model, we select suitable covariates; they include the longitude and latitude of the centroid of the grid cell, the mean elevation of the grid cell, and the mean distance to open sea, following a similar approach adapted by \cite{hrafnkelsson2012spatial} in their work featuring spatial modeling of temperature maxima. The exploratory analysis in Section \ref{sec:EDA} justifies the choice of the covariates. The joint model for the latent layer is represented as
\begin{equation}
    \boldsymbol{\eta} | \boldsymbol{\gamma},\boldsymbol{\Sigma} \sim \mathrm{MVN} (\mathbf{X}\boldsymbol{\gamma},(\mathbf{D-W})^{-1} \otimes \boldsymbol{\Sigma}),
\end{equation}
where $\mathbf{X}$ is the covariate matrix of dimension $1750 \times 35$ in our application, $\boldsymbol{\gamma}$ is the coefficient vector of length $35$, and $\otimes$ denotes the Kronecker product. Here, $\mathbf{X}$ is expressed as
\[
\mathbf{X} =
\left[
\begin{array}{c|c|c|c}
\mathbf{X}_1^\top&\mathbf{X}_2^\top&\cdots&\mathbf{X}_{250}^\top
\end{array}
\right]^\top,
\]
where each block $\mathbf{X}_{i}$ is expressed as $\mathbf{X}_i = \mathbf{I}_{7} \otimes \widetilde{\mathbf{X}}_i^\top$ and $\widetilde{\mathbf{X}}_i =(1,\widetilde{X}_i^{(1)}, \cdots, \widetilde{X}_i^{(4)})^\top$. Here, $\widetilde{\mathbf{X}}_i$ contains all the necessary details about the covariates for grid $g_i$. More specifically, $\widetilde{X}_i^{(1)}$ is latitude corresponding to the centroid of grid $g_i$, $\widetilde{X}_i^{(2)}$ is longitude corresponding to the centroid of grid $g_i$, $\widetilde{X}_i^{(3)}$ is the mean elevation corresponding to the grid $g_i$, and $\widetilde{X}_i^{(4)}$ is the proximate sea distance corresponding to the grid $g_i$; with $ \hspace{1.5mm} g_i \subset \mathcal{D}=g_1 \cup\cdots\cup g_{250}$. Further, $\boldsymbol{\Sigma}$ represents the $7 \times 7$-dimensional cross-component covariance matrix within a particular grid cell, and $\mathbf{W}$ is the symmetric proximity matrix, whose $(i,j)^\text{th}$ element is given by
\begin{equation}\nonumber
    w_{ij}=
    \begin{cases}
        1,& \text{if} \quad g_i \sim g_j \\
        0,&  \text{otherwise},
    \end{cases}
\end{equation}
where $g_i \sim g_j$ represents the adjacency of the grid cells $g_i$ and $g_j$ and $w_{ii} = 0, \hspace{1.5mm} \forall g_i \subset \mathcal{D}$. Here, $\mathbf{D}$ is the diagonal matrix whose diagonal elements represent the total number of adjacent regions to a particular region, i.e., $ d_{ii} = \sum _{j \sim i} w_{ij}, \hspace{1.5mm} \forall g_i,g_j \subset \mathcal{D}$. Finally, we choose weakly-informative conjugate priors for the hyperparameters that the latent variables depend on. We consider a multivariate normal prior for the regression coefficient vector $\boldsymbol{\gamma}$, given by $\boldsymbol{\gamma} \sim \mathrm{MVN}(\mathbf{0},\sigma^{2}_{\boldsymbol{\gamma}}\mathbf{I}_{35})$, and we select an inverse-Wishart prior for the cross-covariance matrix $\boldsymbol{\Sigma}$, given by $\boldsymbol{\Sigma} \sim \mathrm{IW}(\nu,\boldsymbol{\Psi})$, where $\nu$ denotes the degrees of freedom and $\boldsymbol{\Psi}$ is the scale matrix of dimension $7 \times 7$. In our application, we fix $\sigma^{2}_{\boldsymbol{\gamma}} = 100^2$, $\nu=0.1$, and $\boldsymbol{\Psi}=0.1 \mathbf{I}_7$, which ensure the weakly-informative nature of the hyperpriors. After including all the essential modeling details about the data layer (except the shape parameter regularization in the data layer as described in Section \ref{subsec:data_layer}) and also the details about the assigned priors for each layer, the proposed hierarchical Bayesian model is
\begin{equation}\label{eq:overall}
    \begin{split}
    \text{Data layer: } \quad
        & (Y_t(g,0),Y_t(g,1))^\top |\bm{\eta}(g) \overset{\mathrm{ind}}{\sim} \text{BHR} (\bm{\eta}(g)),\\[2mm]
        & \text{where} \hspace{1.5mm} \bm{\eta}(g) = (\alpha_0(g), \alpha_1(g), \beta_0(g), \beta_1(g), \sigma^*(g), \psi(g), \lambda^*(g))^\top,\\[2mm]
        & \text{with} \hspace{1.5mm} g \subset g_1 \cup\cdots\cup g_{250} \subset \mathcal{D}, \hspace{1.5mm} t \in \mathcal{J}=\{1,\cdots,165\}, \\
        \\
    \text{Latent layer: } \quad 
        & \boldsymbol{\eta} | \boldsymbol{\gamma},\boldsymbol{\Sigma} \sim \mathrm{MVN} (\mathbf{X}\boldsymbol{\gamma},(\mathbf{D-W})^{-1} \otimes \boldsymbol{\Sigma}), \\
        \\
    \text{Prior layer: } \quad
        & \boldsymbol{\gamma} \sim \mathrm{MVN}(\mathbf{0},\sigma^{2}_{\boldsymbol{\gamma}}\mathbf{I}_p),~ \boldsymbol{\Sigma} \sim \mathrm{IW}(\nu,\boldsymbol{\Psi}).
    \end{split}
\end{equation}

The notations used in \eqref{eq:overall} are as defined in Sections \ref{subsec:causal_inference} and \ref{subsec:BHM}.

%-------------------------------------------------------------------------------------------------
\section{Bayesian inference and hotspot identification}\label{sec:inference_hotspot}

\subsection{Approximate Bayesian inference method}\label{subsec:ABI}

Here, we adopt a similar approach to \cite{johannesson2022approximate} for Bayesian inference, where we approximate the likelihood function with a Gaussian density and combine it with the latent layer to obtain a Gaussian-Gaussian pseudo-model. Building on this framework and using the proposed model in \eqref{eq:overall} as well as the posterior density expression in \eqref{eq:posterior}, we now show that the posterior density can be written as
\begin{equation}\label{post}
    \pi(\boldsymbol{\eta,\gamma,\Sigma} | \mathbf{y}) \varpropto \pi(\boldsymbol{\Sigma})\pi(\boldsymbol{\gamma})\pi(\boldsymbol{\eta|\gamma,\Sigma)}\pi(\mathbf{y}|\boldsymbol{\eta})
     \varpropto \pi(\boldsymbol{\Sigma})\pi(\boldsymbol{\gamma})\pi(\boldsymbol{\eta|\gamma,\Sigma)}L(\boldsymbol{\eta}|\mathbf{y}),
\end{equation}
where $\mathbf{y}$ denotes the observed data vector combining all grid cells and years, and $L$ denotes the generalized likelihood function, 
%that includes all the prior information about the parameters of the distribution family at the data layer (\cdot|\cdot)
with $L(\boldsymbol{\eta}|\mathbf{y})$ is expressed as 
\begin{equation}\label{eq:Likelihood}
    L(\boldsymbol{\eta}|\mathbf{y}) = \prod_{t=1}^{165} \prod_{i=1}^{250}L((y_t(g_i,0),y_t(g_i,1))'|\boldsymbol{\eta}(g_i)) \pi(\psi(g_i)).
\end{equation}
Here, $\pi(\psi(g_i))$ is as defined in Section \ref{subsec:data_layer} and presented in the right panel of Figure \ref{fig:prior.psi}, and used in regularization in the first stage. To avoid confusion, similar to \cite{johannesson2022approximate}, here we use $\pi(\psi(g_i))$ for regularization in the first stage and then consider an appropriate (ICAR) multivariate Gaussian prior structure for $\psi(g_i)$s in the latent layer as well. One may view the product of these two terms, i.e., $\pi(\psi(g_i))$ for $i=1,\ldots, 250$ and the multivariate Gaussian density as the final prior for $\psi(g_i)$s. Now, the generalized likelihood function is approximated by a Gaussian density having mean $\widehat{\boldsymbol{\eta}}$ and the covariance matrix $\boldsymbol{\Sigma_{\widehat{\eta}}}$, where $\widehat{\boldsymbol{\eta}} = \operatorname*{arg\,max}_{\boldsymbol{\eta}} \log L(\boldsymbol{\eta}|\mathbf{y})$ and $\boldsymbol{\Sigma_{\widehat{\eta}}}$ is the inverse of negative Hessian matrix of $\log L$, evaluated at $\widehat{\boldsymbol{\eta}}$. Then, the approximated likelihood function $\widehat{L}(\widehat{\boldsymbol{\eta}}|\mathbf{y})$ can be written as $\widehat{L}(\widehat{\boldsymbol{\eta}}|\mathbf{y}) = \mathcal{N}(\boldsymbol{\eta} | \widehat{\boldsymbol{\eta}},\boldsymbol{\Sigma_{\widehat{\eta}}})$. Here, $\widehat{\bm{\eta}}$ is a 1750-length vector and $\boldsymbol{\Sigma_{\widehat{\eta}}}$ is a $1750\times1750$-dimensional matrix. However, due to assuming independence across grid cells in the data layer, $\boldsymbol{\Sigma_{\widehat{\eta}}}$ is highly sparse and block diagonal in nature, with 250 blocks each of dimension $7\times7$, corresponding to seven parameters in $\bm{\eta}(g_i)$. Hence, the approximate posterior density can be written as
\begin{equation}\label{apprx-post}
      \pi(\boldsymbol{\eta,\gamma,\Sigma} | \widehat{\boldsymbol{\eta}})
      \varpropto \pi(\boldsymbol{\gamma})\pi(\boldsymbol{\Sigma})\pi(\boldsymbol{\eta|\gamma,\Sigma)}\pi(\widehat{\boldsymbol{\eta}}|\boldsymbol{\eta})
      \varpropto \pi(\boldsymbol{\Sigma})\pi(\boldsymbol{\gamma})\pi(\boldsymbol{\eta|\nu,\Sigma)}\mathcal{N}(\boldsymbol{\eta} | \widehat{\boldsymbol{\eta}},\boldsymbol{\Sigma_{\widehat{\eta}}}).
\end{equation}
This approximation by $\pi(\boldsymbol{\eta,\gamma,\Sigma} | \widehat{\boldsymbol{\eta}})$ to our exact posterior density $\pi(\boldsymbol{\eta,\gamma,\Sigma} | \mathbf{y})$ leverages conjugacy, making posterior inference easier and faster than with the exact model. Here, we apply the Bayesian inference scheme proposed by \cite{hrafnkelsson2021max}, i.e., Max-and-Smooth, where the process of approximating the generalized likelihood function with a Gaussian density with mean $\widehat{\boldsymbol{\eta}}$ and the covariance matrix $\boldsymbol{\Sigma_{\widehat{\eta}}}$ refers to the Max-step and inference of the latent variables and hyperparameters, and smoothening the latent surface using the Gaussian-Gaussian pseudo model refers to the Smooth-step. The advantages of the Max-and-Smooth approach are that the computational cost of implementing a Markov chain Monte Carlo (MCMC) algorithm remains roughly constant even as the number of independent replications (here, years) of the observed data increases. Besides, the sparse precision matrix of the Gaussian prior density is beneficial for computational efficiency. 

%-------------------------------------------------------------------------------------

\subsection{MCMC implementation} \label{subsec:mcmc}
Obtaining the Gaussian-Gaussian pseudo-model as the end product of the extended Max-and-Smooth approach, along with reasonable prior choices for hyperparameters, enables us to implement Gibbs sampling to draw posterior inference about the latent variables and hyperparameters. While updating $\boldsymbol{\eta}$ of length 1750 using Gibbs sampling, the sparse precision matrix of Kronecker-form and the sparse structure of $\mathbf{X}$ enable using the \texttt{R} package \texttt{spam} \citep{furrer2010spam}, and its appropriate tools drastically increase the speed of the Gibbs sampling steps. Similarly, while updating $\boldsymbol{\gamma}$, we rely on the \texttt{spam} package for boosting the speed up due to the involvement of $\mathbf{X}$ in it. The conjugacy feature, enabled by the inverse-Wishart prior for $\boldsymbol{\Sigma}$, facilitates Gibbs sampling updates for it. Overall, our proposed model provides closed-form expressions for the full conditional posterior distributions of all model parameters and hyperparameters, thereby avoiding any Metropolis-Hastings steps. The full conditional posteriors (FCPs) for updating $\boldsymbol{\eta}$ of length 1750, $\boldsymbol{\gamma}$ of length 35, and $\boldsymbol{\Sigma}$ of dimension $7\times 7$ in our Gibbs sampling scheme are as follows:
\begin{itemize}
    \item Simulate $\boldsymbol{\eta}$ from the FCP of $\bm{\eta}$, given by $\boldsymbol{\eta}|\mathbf{y},\mathbf{X},\boldsymbol{\gamma},\boldsymbol{\Sigma} \sim \mathrm{MVN} (\boldsymbol{\mu}_{\boldsymbol{\eta}}^{\text{post}},\boldsymbol{\Sigma}_{\boldsymbol{\eta}}^{\text{post}})$,  where\\$\boldsymbol{\mu}_{\boldsymbol{\eta}}^{\text{post}}=\boldsymbol{\Sigma}_{\boldsymbol{\eta}}^{\text{post}} (\boldsymbol{\Sigma}_{\widehat{\boldsymbol{\eta}}}^{-1}\widehat{\boldsymbol{\eta}}+[(\mathbf{D}-\mathbf{W})\otimes \boldsymbol{\Sigma}^{-1}] \mathbf{X}\boldsymbol{\gamma})$ and  
    $\boldsymbol{\Sigma}_{\boldsymbol{\eta}}^{\text{post}} = (\boldsymbol{\Sigma}_{\widehat{\boldsymbol{\eta}}}^{-1} +(\mathbf{D}-\mathbf{W}) \otimes \boldsymbol{\Sigma}^{-1})^{-1}$,
    \item Simulate $\boldsymbol{\gamma}$ from its FCP, $\boldsymbol{\gamma}|\boldsymbol{\eta},\mathbf{X},\boldsymbol{\Sigma}  \sim \mathrm{MVN} (\boldsymbol{\mu}_{\boldsymbol{\gamma}}^{\text{post}},\boldsymbol{\Sigma}_{\boldsymbol{\gamma}}^{\text{post}})$, where \\
    $\boldsymbol{\mu}_{\boldsymbol{\gamma}}^{\text{post}} = \boldsymbol{\Sigma}_{\boldsymbol{\gamma}}^{\text{post}} (\mathbf{X}^\top [(\mathbf{D}-\mathbf{W})\otimes \boldsymbol{\Sigma}^{-1}]\boldsymbol{\eta})$ and $\boldsymbol{\Sigma}_{\boldsymbol{\gamma}}^{\text{post}} = 
    (\mathbf{X}^\top[(\mathbf{D}-\mathbf{W})\otimes\boldsymbol{\Sigma}^{-1}]\mathbf{X}+\sigma^{-2}_{\boldsymbol{\gamma}}\mathbf{I}_{35})^{-1}$,
    \item Simulate $\boldsymbol{\Sigma}$ from its FCP, $\boldsymbol{\Sigma}|\boldsymbol{\eta},\mathbf{X},\boldsymbol{\gamma} \sim \text{IW} (\nu^{\text{post}}, \boldsymbol{\Psi}^{\text{post}})$, where \\
    $\nu^{\text{post}}=\nu+|\mathcal{I}|$ and $\boldsymbol{\Psi}^{\text{post}}= \operatorname{vec}^{-1}(\boldsymbol{\eta}-\mathbf{X}\boldsymbol{\gamma})(\mathbf{D}-\mathbf{W}) (\operatorname{vec}^{-1}(\boldsymbol{\eta}-\mathbf{X}\boldsymbol{\gamma}))^\top + \boldsymbol{\Psi}$.    
\end{itemize}
Here, $\operatorname{vec}^{-1}$ converts the vector $\boldsymbol{\eta}-\mathbf{X}\boldsymbol{\gamma}$ of length 1750 into a $7\times 250$ matrix, with the first seven entries of the vector forming the first column of the matrix, the next seven entries forming the second column of the matrix, and so on. In our data application, we implement the MCMC algorithm in \texttt{R} (\hyperlink{http://www.r-project.org/}{http://www.r-project.org/}). We generate $60,000$ posterior samples and discard the first $10,000$ samples as burn-in. After choosing the thinning equal to $5$, that is, keeping one out of every five consecutive samples of the Markov chain, we are left with $10,000$ samples. These $10,000$ samples are used for drawing posterior inference. The convergence and mixing of the chains are well-examined through their trace plots, Geweke statistics, and Gelman-Rubin diagnostics.
%-------------------------------------------------------------------------------------

\subsection{Hotspot estimation} \label{subsec:hotspot}

In addition to estimating the effect of human intervention on high temperature extremes, our goal is to identify the regions at risk, that is, to construct a credible region that contains the true exceedance set with a specified level of probability. Here, the true exceedance set refers to the collection of grid cells where the estimated treatment effect exceeds the chosen threshold. We adapt the proposal based on the Bayesian setting of \cite{french2016credible} for outer credible region construction, which is the natural extension of the frequentist setting proposed by \cite{french2013spatio}. The primary reason for deploying the sampling-based methodology of \cite{french2016credible} is that it is easy to implement, as it relies on samples from the posterior predictive distribution generated by MCMC methods.

Let $ s_{g_i}$ be the centroid, which is also known as the representative location, corresponding to the grid $g_i$, where $i \in \mathcal{I}=\{1,\cdots,250\}$. For an user-defined threshold $u$, the true exceedance region is defined as $E_{u^+}= \{g: \delta(s_g) > u \}$, where $\delta(\cdot)$ is the causal effect and $u$ is the chosen threshold. Our goal is to construct the outer-credible region, i.e., $C_{u^+}^{O} (\alpha)$ such that $\mathrm{P}(E_{u^+} \subset C_{u^+}^{O} (\alpha)) = 1-\alpha$. The bridge between obtaining samples from the posterior predictive distribution and constructing $C_{u^+}^{O}$ is built on a multiple-hypothesis testing procedure. However, the outer credible region $C_{u^+}^{O}$ is not unique and depends on the discretization of the domain of interest. For a gridded dataset like ours, the discretization is pre-specified. A major drawback of testing $H_0(s_g):\delta(s_g) \geq 0$ versus $H_1(s_g):\delta(s_g) < 0$ individually in each grid cell based on some decision rule $\phi(s_g)$, which depends upon the test statistics $T(s_g)$ with predefined confidence level $1-\alpha$, is the failure in accurate representation of joint threshold exceedances. To address this issue, we perform multiple hypothesis testing by selecting a suitable critical value that controls the family-wise error rate at level $\alpha$. In our analysis, to perform the multiple hypothesis testing, we choose the grid cell-wise test statistics
\begin{equation}
    T(s_g)=\frac{\mathbb{E}(\delta(s_g)|\mathbf{y})-u}{\sqrt{\mathbb{E}((\delta(s_g)-u)^2|\mathbf{y})}}.
\end{equation}
The detailed description of the algorithm for estimating the region containing the true joint outer exceedance region, i.e., $C_{u^+}^{O} (\alpha)$, is given in Algorithm \ref{alg:alg1}.

\begin{algorithm}[t] 
    \caption{Hotspot estimation algorithm \citep{french2016credible}}
    \label{alg:alg1}
    \begin{itemize}
        \item Fix the threshold level $u$ and the family-wise error rate $\alpha$.
        \item Obtain $B$ MCMC samples from the approximate posterior (using Max-and-Smooth) corresponding to the latent variables and hyperparameters.
         \item for each posterior samples $b \in \{1,\cdots,B\}$:
         \begin{itemize}
             \item Retrieve posterior samples  $\alpha_0^{(b)}(s_g),\beta_0^{(b)}(s_g),\alpha_1^{(b)}(s_g),\beta_1^{(b)}(s_g)$, where $g \subset \mathcal{D}$.
             \item Calculate $\delta^{(b)}(s_g)$ using \eqref{pRTE_apprx}.
         \end{itemize}
        \item Calculate the test statistics corresponding to each grid, i.e., $T(s_{g_{1}}),\cdots,T(s_{g_{250}})$.
        \item Using $\widetilde{\delta}^{(b)}$, where $\widetilde{\delta}^{(b)} = \{ \delta^{(b)}(s_{g_{1}}),\cdots,\delta^{(b)}(s_{g_{250}})\}$ and $b \in \{1,\cdots,B\}$:
        \begin{itemize}
            \item Identify the exceedance set above the threshold $u$, i.e., $E_{u^+}^{(b)}=\{g_i:\delta^{(b)}(s_{g_{i}}) \geq u, ~i\in\{1,\cdots,250\} \}.$
            \item Determine $\mathcal{M}^{(b)}$, where $\mathcal{M}^{(b)}=\text{min}\{T(s_g);g \in E_{u^+}^{(b)}\}$. Set $\mathcal{M}^{(b)} = 0$, if $E_{u^+}^{(b)}$ is empty.
        \end{itemize}
        \item Estimate the critical value $c(\alpha)$ using the $\alpha$-quantile of $\{ \mathcal{M}^{(1)},\cdots,\mathcal{M}^{(B)}\}.$
        \item Obtain $C_{u^+}^{O}$, where $C_{u^+}^{O} (\alpha) =\{g_i:T(s_{g_{i}})\geq \widehat{c}(\alpha)\}$.
    \end{itemize}
\end{algorithm}
%-------------------------------------------------------------------------------------------------
\section{Data application}\label{sec:data_application}

We fit the proposed Bayesian hierarchical model in Section \ref{subsec:BHM} to the climate model output described in Section \ref{sec:EDA}. Utilizing the approximate Bayesian inference method in Section \ref{subsec:ABI}, we obtain $10,000$ posterior samples for each latent variable and hyperparameter. Although trace plots of Markov chains for different parameters are widely used to assess convergence and mixing, practitioners often use multiple diagnostic tools to assess convergence and shed light on the quality of posterior samples. Given that the number of latent variables and hyperparameters is high in our model, we focus on the diagnostics for the hyperparameter vector $\bm{\gamma}$. Gelman-Rubin diagnostics, denoted by $R$-value, assess the quality of posterior samples and indicate agreement between posterior means across multiple chains; we obtain the estimated $R$-value, i.e., $\widehat{R}$ and its upper confidence limit for each MCMC chain. Generally, $\widehat{R}=1$ indicates convergence of the chain, and a value of $\widehat{R}>1.1$ indicates questionable convergence \citep{reich2019bayesian}. In our case, the $\widehat{R}$ values are equal to 1, and also the upper confidence limits are equal to 1 for all the hyperparameters in $\boldsymbol{\gamma}$; they signify the convergence of MCMC chains. Further, Geweke's diagnostic is also intended to assess the convergence of the Markov chains for the hyperparameters in $\boldsymbol{\gamma}$. Geweke's statistic is essentially a $z$-score that signifies the difference between the sample means of two subsequences of the Markov chain, divided by the estimated standard error. Hence, an absolute value of the score below 1.96 indicates convergence of the Markov chain. The calculated Geweke's statistics for all the hyperparameters stored in $\boldsymbol{\gamma}$ are reported in the top block of Table~\ref{Geweke_ESS_combined}. The score values lie within the 0.025$\mathrm{th}$ and 0.975$\mathrm{th}$ standard normal quantiles for all considered hyperparameters, indicating that the MCMC chains have converged after the burn-in period. Further, the Effective sample size (ESS) quantifies the number of independent samples that contain the same information as the total number of correlated samples in the Markov chain. These pseudo-independent samples are used to improve the uncertainty assessment of the posterior mean calculated from posterior samples. In the bottom block of Table \ref{Geweke_ESS_combined}, the ESS of all 35 hyperparameters in $\boldsymbol{\gamma}$ are reported. Overall, the ESS values are on the higher side for all the model hyperparameters except one coefficient related to $\lambda^*$. All the desired metrics obtained from diagnostic tools, such as Geweke's statistic, Gelman-Rubin statistics, and reported higher ESS values, collectively imply the good quality of the posterior samples used for drawing posterior inference.

\begin{table}[h]
\centering
\caption{Geweke $z$-scores (top) and effective sample sizes (bottom) for all hyperparameters in $\boldsymbol{\gamma}=(\boldsymbol{\gamma}_{\alpha_{0}},\boldsymbol{\gamma}_{\alpha_{1}},\boldsymbol{\gamma}_{\beta_{0}},\boldsymbol{\gamma}_{\beta_{1}},\boldsymbol{\gamma}_{\sigma^{*}},\boldsymbol{\gamma}_{\psi},\boldsymbol{\gamma}_{\lambda^*})'$, where $\boldsymbol{\gamma}_{\textit{j}} = (\gamma^{(1)}_{\textit{j}},\gamma^{(2)}_{\textit{j}},\gamma^{(3)}_{\textit{j}}, \gamma^{(4)}_{\textit{j}}, \gamma^{(5)}_{\textit{j}})', \forall \textit{j} \in \{ \alpha_{0},\alpha_1,\beta_0,\beta_1,\sigma^*,\psi,\lambda^*\} $. Here, each element of the table corresponds to the Geweke statistic or the effective sample size for a specific component of the vector of covariate coefficients associated with latent variables.}
\begin{tabular}{|l|ccccccc|}
%\hline
\multicolumn{1}{c}{}
 &
$\boldsymbol{\gamma}_{\alpha_0}$ &
$\boldsymbol{\gamma}_{\beta_0}$ &
$\boldsymbol{\gamma}_{\alpha_1}$ &
$\boldsymbol{\gamma}_{\beta_1}$ &
$\boldsymbol{\gamma}_{\sigma^*}$ &
$\boldsymbol{\gamma}_{\psi}$ &
\multicolumn{1}{c}{$\boldsymbol{\gamma}_{\lambda^*}$} \\
    \hline
\multicolumn{8}{|c|}{Geweke $z$-scores} \\
\hline
$\gamma^{(1)}$ & -0.46 & 0.45 & 0.13 & -0.42 & -0.97 & -0.45 & 0.19\\
$\gamma^{(2)}$ & 0.58 & -0.60 & 0.71 & 1.81 & -0.66 & 1.32 & 0.30 \\
$\gamma^{(3)}$ & -0.41 & -0.08 & -0.37 & -0.35 & 1.97 & 0.07 & 0.17 \\
$\gamma^{(4)}$ & 0.81 & 0.55 & 0.88 & -0.11 & -0.47 & 0.59 & 1.52 \\
$\gamma^{(5)}$ & 0.30 & 0.05 & 0.34 & 0.94 & -1.41 & 0.22 & -0.66 \\
%$\gamma^{(6)}$ & -0.18 & 0.85 & -0.23 & 0.09 & -0.53 & 0.01 & -1.07 \\
\hline
\multicolumn{8}{|c|}{Effective Sample Size (ESS)} \\
\hline
$\gamma^{(1)}$ & 12000 & 12000 & 12000 & 12000 & 12000 & 12000 & 12000 \\
$\gamma^{(2)}$ & 12000 & 12000 & 12000 & 12000 & 10576 & 12000 & 3863 \\
$\gamma^{(3)}$ & 12000 & 11389 & 12000 & 12000 & 8365 & 9560  & 2689 \\
$\gamma^{(4)}$ & 12000 & 5712 & 12000 & 12000 & 2326 & 2764 & 702 \\
$\gamma^{(5)}$ & 12000 & 10696 & 12000 & 12000 & 5770 & 7978 & 1952 \\
%$\gamma^{(6)}$ & 12000 & 9908 & 12000 & 12000 & 5330 & 12000 & 1274 \\
\hline
\end{tabular}
\label{Geweke_ESS_combined}
\end{table}

Before moving to discussing inferences about the grid cell-level parameters, we summarize the posterior means and standard deviations of all model hyperparameters in $\boldsymbol{\gamma}$ in Table \ref{post_mean_latent}. The intercept terms have very large posterior standard deviations relative to their means, indicating substantial uncertainty and suggesting weak identifiability or limited information in the data regarding baseline effects. In contrast, covariates such as longitude and latitude demonstrate pronounced and consistent effects across most latent variables, with relatively smaller standard deviations, underscoring their strong spatial influence. Latitude, in particular, is associated with large magnitude coefficients and moderate uncertainty, reflecting a dominant north–south gradient. Mean elevation (ME) exhibits stable and precisely estimated effects, as indicated by very small standard deviations, which demonstrates a robust and consistent contribution across components. Open sea distance (OS) also displays clear effects, though with slightly higher variability than ME, suggesting a moderate influence with some uncertainty. Collectively, these results indicate that spatial covariates, especially latitude and longitude, are key components of the latent structure, while elevation provides a steady contribution, and intercept terms remain weakly identified.

\begin{table}[h]
    \centering
    \caption{Posterior means and standard deviations (within brackets) of all the hyperparameters stored in $\bm{\gamma}$. Here, different columns represent the posterior means and standard deviations of the covariate coefficients for different latent variables. Each row represents the posterior means and standard deviations of the coefficients for a specific covariate. Here, Int denotes the intercept, Lon denotes the Longitude, Lat denotes the latitude, ME denotes the mean elevation, and OS denotes the open sea distance. }
    \setlength{\tabcolsep}{0.3pt}
    \begin{tabular}{|l|c|c|c|c|c|c|c|}
    \multicolumn{1}{c}{}&
    $\alpha_0$ &  
    $\alpha_1$ &
    $\beta_0$ &
    $\beta_1$ &
    $\sigma^*$ &
    $\psi$  &
    \multicolumn{1}{c}{$\lambda^*$} \\
    \hline   
    Int   & -1.53(99.07)  & 19.41(101.13) & -4.07(100.15)  & -4.83(99.09)  & 2.43 (100.19) & -8.67(99.41)  & -9.41(100.63)\\
    Lon   &-455.0(50.27)  &14.29(2.57) &-438.87(49.56) &-8.63(4.41)  &-71.60(3.88)  &30.79(2.27) & 44.39(6.52)\\
    Lat  &-3654.42(56.45)  & 82.74(3.47)  &-3829.63(55.82)  &72.23(5.05)  &140.55(5.46)  &80.31(3.01)  &85.87(12.01)\\
    ME   &-51.40(0.21)  &0.17(0.02) &-50.39(0.20)  &0.17(0.02)  &-1.75(0.04) &0.13(0.01)  &0.85(0.09)\\
    %SE    &7.39(0.66)  &-0.25(0.08)  &8.67(0.65)  &-0.07(0.06)  &-1.70(0.18)  & -0.01(0.03)  &0.11(0.47)\\
    OS   &30.66(0.66)  &0.51(0.04) &28.28(0.65)  &-2.15(0.06)  &1.83(0.07)  &-0.94(0.04)  &-1.65(0.14)\\
    \hline
    \multicolumn{8}{l}{\footnotesize Here, expect the elements of the first row, elements of all the remaining rows are multiplied by $10^{3}$.}
    \end{tabular}
    \label{post_mean_latent}
\end{table}

Our primary goal is to estimate the effect of human intervention on high temperature extremes using the causal metric defined in \eqref{pRTE}. Hence, we utilize the posterior samples of $\alpha_0,\alpha_1,\beta_0,~\text{and}~\beta_1$ to estimate the causal effect, given their role in the final expression of the causal metric. We calculate posterior estimates of the causal effect for each grid that jointly constitute the domain of interest, i.e., the mainland United States. 
\begin{figure}[t]
  \centering %, height = 4.5cm
  \includegraphics[width=\textwidth]{causal_effect_USA_plot.pdf}
  \caption{Grid cell-wise posterior means (left) and posterior standard deviations (right) of the causal effect. }
  \label{causal_effect_plot}
\end{figure}
The spatial map of the grid cell-wise posterior means of the causal effect is displayed in the left panel of Figure \ref{causal_effect_plot}. Alongside that, the spatial map of the grid cell-wise posterior standard deviations calculated using posterior samples of causal effects is shown in the right panel of Figure \ref{causal_effect_plot}. From this figure, it is evident that in most regions of the mainland United States, the effect of anthropogenic forcing on high-temperature extremes is positive. In the northeast region and some parts of the southern region, including the South Atlantic and the East South Central division, the causal effect estimate is higher than in all other regions, with the estimated mean causal effect ranging from $0.20$ to $0.50$. In the West region, the West South Central and East North Central divisions, the mean causal effect lies between $0$ and $0.3$, while in a fraction of the subregions it is approximately $0.5$. Nevertheless, in the West North Central division of the Midwest region, which includes North Dakota, Minnesota, South Dakota, Nebraska, some parts of Iowa, and Montana, the posterior mean of the causal effect is negative. While the positive effect implies a significant contribution of anthropogenic forcing to the frequent occurrence of high-temperature extremes, the negative effect implies no such contribution. According to the CENSUS report \citep{hartley2021preliminary}, the major parts of the midwestern states where the estimated causal effect is negative are sparsely populated due to several reasons, including harsh climate conditions, and the agricultural and grazing land covers a substantial portion of the land in the Midwestern region containing North Dakota, South Dakota, Nebraska, and Iowa \citep{pryor2013midwestern}. Natural forcing, such as atmospheric circulation patterns and solar radiation, has a greater impact on the occurrence of high-temperature extremes \citep{andresen2012historical} in these regions than human-induced forcing, such as greenhouse gas emissions. However, the northeastern region, with major metropolitan cities, and the states in the South Atlantic division are densely populated \citep{fonseca2000changing}, which implies land-use change and urbanization and leads to anthropogenic forcing acting as a key contributor to the warmer climate in those areas.
\begin{figure}[t]
  \centering %, height = 4.5cm
  \includegraphics[width=\textwidth]{causal_effect_USA_pi_plot.pdf}
  \caption{Grid cell-wise posterior means (left) and posterior standard deviations (right) of the causal effect during the pre-industrial period (1850--1900).}
  \label{causal_effect_plot_pi}
\end{figure}

Generally, the period $1850-1900$ is considered the pre-industrial era and is used as a baseline for climate change assessment studies. Figure \ref{causal_effect_plot_pi} displays the spatial maps of the posterior mean causal effect across the mainland United States during this pre-industrial period. The estimated causal effect is negative in most regions of the mainland United States. The comparison between the spatial maps of the estimated causal effect over the whole time period and only the pre-industrial period shows that anthropogenic forcing is a significant contributor to the recurrence of high-temperature extremes.
\begin{figure}[t] %, height = 8.5cm
  \centering
  \includegraphics[width=\textwidth]{causal_effect_USA_trend_plot.pdf}
  \caption{Grid cell-wise posterior means (top-left) and posterior standard deviations (top-right) of the trend (the change in the intensity of high-temperature extremes per unit change in year) for the factual world, and the pixel-wise posterior means (bottom-left) and posterior standard deviations (bottom-right) of the trend difference between the factual and counterfactual worlds.}
  \label{trend_USA_plot}
\end{figure}

The extensive information on the trend of high-temperature extremes helps in designing more effective adaptation and mitigation policies to address them to some extent. Here, the trend is defined as the change in the intensity of high-temperature extremes per unit change in year. We turn to $\alpha_1$ and $\beta_1$ to understand the trend behavior in both counterfactual and factual worlds. Hence, the spatial map of the posterior means of $\beta_1$ is shown in the left panel of Figure \ref{trend_USA_plot}, which presents the trend in the factual world. In addition to this, the spatial map of corresponding standard deviations is also displayed in the right panel of Figure \ref{trend_USA_plot}. In the factual world, the Midwestern region exhibits a negative trend in high-temperature extremes over the year, while all other regions show a positive trend in their intensity due to rapid urbanization, industrial exposure, and land-use changes. Stakeholders and climate policymakers may be highly interested in the observed trend in the factual world. However, the changes in trends of both counterfactual and factual worlds are also shown in Figure \ref{trend_USA_plot}. From the perspective of highlighting the significant contribution of anthropogenic forcing to the intensification of temperature extremes across most regions of the mainland United States, excluding the Midwest, the trend-difference spatial map is considered important. Alongside that, the spatial map of the corresponding standard deviations is presented in Figure \ref{trend_USA_plot}. % in the form of a spatial surface plot.
\begin{figure}[t]
  \centering
  \includegraphics[width = \textwidth, height = 4.5cm]{Hotspot_USA_plot.pdf}
  \caption{Estimated $95\%$ credible regions $C_{u^{+}}^{O}$ corresponding to the joint exceedance levels, $u = 0.35$ (left) and $u=0.65$ (right).}
  \label{hotspot_USA_plot}
\end{figure}

Considering the importance of identifying regions at risk, we estimate the outer credible region using the hotspot region estimation technique given in Section \ref{subsec:hotspot}. We construct $95\%$ credible regions $C_{u^{+}}^{O}$ corresponding to high threshold levels, $u =0.35$ and $u=0.65$. Figure \ref{hotspot_USA_plot} shows the hotspot regions over the mainland United States. For $u=0.35$, the estimated credible region spans the Northeast, South, and West regions, excluding the northern and eastern parts of Montana and small portions of Wyoming and Colorado. When considering the joint exceedance level $ u=0.65$, the proportion of the coverage area decreases significantly compared to $u=0.35$. The estimated credible region, choosing $u=0.65$, covers a narrow region in the Northeastern part of the mainland United States, including New Jersey, New York, Pennsylvania, and the District of Columbia, as well as Maryland and some portions of Virginia and North Carolina in the southern region. The estimated hotspot regions include $66\%$ and $9.6\%$ of the total number of grid cells under the two considered thresholds. Although in most regions of the mainland United States the effect of anthropogenic forcing on high-temperature extremes is positive, identifying regions that need immediate action to achieve a sustainable climate may be of high importance to stakeholders and climate policymakers. In this context, to identify the regions that need immediate attention in implementing the regulation policy governing human intervention, hotspot regions are constructed using high thresholds.

\section{Discussion}\label{sec:discussion}

Considering the high applicability of extreme event attribution studies during this alarming phase of climate change, we propose a novel causal metric to quantify the impact of anthropogenic forcing on high-temperature extremes, which will be useful for climatologists working in detection and attribution. This causal metric is developed on top of a unified potential outcome framework that integrates the marginal return levels of annual temperature maxima of both the counterfactual and factual worlds. Besides, it has a valid causal interpretation under unconfounding and in the absence of interference, and we use it to estimate the effect of anthropogenic forcing on high-temperature extremes across the mainland United States.

We employ a latent Gaussian model (LGM), a special class of Bayesian hierarchical model, to correctly specify the marginal return levels and the uncertainties associated with the latent variables and hyperparameters. In the data layer, we model annual temperature maxima using GEV distributions with spatially-varying coefficients, with the temporal component incorporated into the location parameter. We propose a novel transformation for the shape parameter $\xi$ based on three reasonable conditions in the context of temperature extremes. We assert that the transformation method is reliable when specifically applied to high-temperature extremes. From an application perspective and for reliable tail inference, we propose a transformed asymmetric density for $\xi$ \citep{martins2000generalized}. In the latent layer, we employ the ICAR model to capture the conditional neighborhood effect and to smooth the spatial surfaces of posterior estimates. In addition, the conditional autoregressive model features a precision matrix that encodes conditional dependence information, allowing faster Bayesian computation and opening the door to the applicability of sampling-based inferential schemes, such as MCMC methods. We employ an extended version \citep{johannesson2022approximate} of the Max-and-Smooth approach \citep{hrafnkelsson2021max} to bypass the complex posterior computations. The proposed LGM, along with the approximate Bayesian inference scheme, leverages Gibbs sampling to draw posterior inference about the latent variables before other complex MCMC methods. After drawing posterior samples of the corresponding latent parameters used in the causal metric, we obtain the estimated spatial surface of the causal effect over the contiguous United States. A spatial plot of the posterior estimate of the causal effect shows that anthropogenic forcing is more active than other factors in driving frequent high-temperature extremes across the Northeastern region, including most metropolitan cities across the mainland United States. Furthermore, this attribution study unveils the trend in temperature extremes and the effectiveness of anthropogenic forcing in driving it during the pre-industrial period over the mainland United States. Using posterior causal effect estimates and a suitable threshold, the hotspots are constructed over the mainland United States using the approach in \cite{french2016credible}, controlling the family-wise error rate (FWER). The outer credible region corresponding to a high threshold displayed in the study includes the majority of the Northwestern region and a fraction of the Southwestern region, which needs attention. While we focus on the outer credible region, an estimated inner credible region turns out to be a null set; the availability of a dataset with a higher resolution than $1^\circ \times 1^\circ$ would facilitate such an analysis as well.

In our methodology and computation for obtaining efficient marginal return level estimates, implementing approximate rather than exact Bayesian inference and ignoring extremal dependence in the data layer are possible drawbacks. Given that we have a sufficiently large number of temporal observations (165, here) at each grid cell to estimate only four parameters of the marginal distributions, a Laplace approximation of the data likelihood seems reasonable. However, in applications with a very limited number of temporal replications, a Laplace approximation may not be particularly suitable, and replacing the block maxima approach with a peaks-over-threshold or point process approach \citep{hazra2023bayesian} would be a more reasonable option. As noted by \cite{davison2012statistical}, LGMs perform reasonably well for estimating return levels, and thus our methodology may not be suitable for exploring spatial dependence properties. In such a case, a proper max-stable model \citep{schlather2002models, padoan2010likelihood, reich2012hierarchical,huser2024vecchia} would be a more reasonable approach. Another interesting research direction would be incorporating the Whittle-Matérn Brown-Resnick process, recently proposed by \cite{bolin2025intrinsic} for modeling temperature maxima, which is based on a new flexible class of intrinsic Whittle-Mat\'ern Gaussian random fields and facilitates sparse computation. Recently, \cite{cotsakis2026assessing} provided informative metrics based on excursion sets, and metrics inferred from estimated hotspots can provide meaningful insights to policymakers.

\section*{Data and code availability}
The \texttt{R} code and data required to reproduce the figures and tables presented in this article are accessible at the following GitHub repository: \url{https://github.com/ritik-76/Causal_attribution}.

\bibliographystyle{plainnat} % try: abbrvnat, unsrtnat, etc.
\bibliography{main}          % refs.bib (no extension)

\end{document}
