\documentclass[10pt,prd,nofootinbib,preprint]{revtex4}
\usepackage[a4paper, total={7in, 10.5in}]{geometry}
\usepackage[utf8]{inputenc}
\setcounter{secnumdepth}{3}
\usepackage{bm}
\usepackage{color}
\usepackage{xcolor}
\usepackage{float}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{esint}
\usepackage{epsfig}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{hyperref}
\usepackage{cancel}
\makeatletter

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% LyX-specific LaTeX commands.
\DeclareFontEncoding{LGR}{}{}
\DeclareRobustCommand{\greektext}{%
  \fontencoding{LGR}\selectfont\def\encodingdefault{LGR}}
\DeclareRobustCommand{\textgreek}[1]{\leavevmode{\greektext #1}}
\ProvideTextCommand{\~}{LGR}[1]{\char126#1}

\newcommand{\lyxmathsym}[1]{\ifmmode\begingroup\def\b@ld{bold}
  \text{\ifx\math@version\b@ld\bfseries\fi#1}\endgroup\else#1\fi}

%% Because html converters don't know tabular newline
\providecommand{\tabularnewline}{\\}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Text-class-specific LaTeX commands.
\@ifundefined{textcolor}{}
{%
 \definecolor{BLACK}{gray}{0}
 \definecolor{WHITE}{gray}{1}
 \definecolor{RED}{rgb}{1,0,0}
 \definecolor{GREEN}{rgb}{0,1,0}
 \definecolor{BLUE}{rgb}{0,0,1}
 \definecolor{CYAN}{cmyk}{1,0,0,0}
 \definecolor{MAGENTA}{cmyk}{0,1,0,0}
 \definecolor{YELLOW}{cmyk}{0,0,1,0}
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% user specified LaTeX commands.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\usepackage{xcolor}
\usepackage{epsfig}\usepackage{slashed}\usepackage{appendix}
\usepackage{tabularx}
\usepackage{pdfpages}
\usepackage{epstopdf}
%\usepackage{subfigure}
\usepackage{multirow}
\usepackage{siunitx}
\usepackage{soul}
 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%new
\usepackage[T1]{fontenc}
%\usepackage[latin9]{inputenc}
%\usepackage{array}
%\usepackage{booktabs}
%\usepackage{amstext}
%\usepackage{babel}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%new
%\makeatother
%\renewcommand{\textcolor}[2]{#2}
\begin{document}
\begin{center}
{\bf\Large\boldmath
%Global fit of B anomalies with implications via  $\Lambda_{b}\rightarrow\Lambda_{c}\tau\bar{\nu}_{\tau}$ five-fold distributions
The Angular Observables of 
$\Lambda_b \to \Lambda_c(\to \Lambda^0 \pi^+) \, 
\tau^-(\to \pi^- \nu_\tau)\, \bar{\nu}_\tau$ 
within the Paradigm of FCCC Anomalies
}\\[5mm]
\par\end{center}
\begin{center}
\setlength{\baselineskip}{0.2in} {Muhammad Arslan$^{a,}$\footnote{arslan.hep@gmail.com (corresponding author)},
Ishtiaq Ahmed$^{b,}$\footnote{ishtiaqmusab@gmail.com} and Muhammad Jamil Aslam $^{a,}$\footnote{jamil@qau.edu.pk}
%, Saba Shafaq$^{c,}$\footnote{saba.shafaq@iiu.edu.pk}  and Tahira Yasmeen$^{c,}$\footnote{tahira709@gmail.com}
}\\[5mm] $^{a}$~\textit{Department of Physics, Quaid-i-Azam
University, Islamabad 45320, Pakistan.}\\
 $^{b}$~\textit{National Center for Physics, Islamabad 44000, Pakistan.}\\[5mm]
% $^{c}$~\textit{Department of Physics, International Islamic University,
%Islamabad 44000, Pakistan.}\\[5mm] 
\par\end{center}

\begin{abstract}
We present a global analysis of the current $B$-meson flavor anomalies and extend it to the baryonic sector through the decay $\Lambda_b^0 \to \Lambda_c^+(\to \Lambda^0 \pi^+) \tau^-(\to \pi^- \nu_\tau)\bar{\nu}_\tau$. The lepton flavor universality ratios $R_{\tau/(\mu,e)}(D^{(*)})$, measured by BaBar, Belle, and LHCb, exhibit a combined $3.8\sigma$ deviation from Standard Model (SM) predictions. Using the latest HFLAV averages and imposing $B_c$-lifetime constraints on the branching ratio, $\mathcal{B}(B_c \to \tau \nu) < 60\%, 30\%, 10\%$, we perform a global fit to the anomaly data and propagate the preferred new physics (NP) solutions to the full cascade decay $\Lambda_b^0 \to \Lambda_c^+(\to \Lambda^0 \pi^+) \tau^-(\to \pi^- \nu_\tau)\bar{\nu}_\tau$. The mixed vector-scalar scenario $(C_{V_L},C_{S_R})$ emerges as the most favored NP solution, yielding the largest pull from the SM while remaining insensitive to branching-ratio constraints. The single-operator $C_{V_L}$ case identified as the next most competitive scenario. We study the impact of NP vector, scalar and tensor operators on a complete set of angular observables on the five-fold $\Lambda_b$ decay using Lattice-QCD form factors and find that the scenarios $(\Re[C_{S_L}=4C_T],\Im[C_{S_L}=4C_T])$ and $(C_{S_L},C_{S_R})$ generate the largest deviations from the SM predictions. In particular, the observables $\mathcal{K}_{1c}$, $\mathcal{K}_{2ss}$, $\mathcal{K}_{2cc}$, and $\mathcal{K}_{4s}$ show the highest sensitivity to NP effects. The correlation analysis reveals distinctive NP patterns: the $(\Re[C_{S_L}=4C_T],\Im[C_{S_L}=4C_T])$ scenario exhibits inverse correlations among $\mathcal{K}_{1c}$ and $\mathcal{K}_{2ss,2cc,4s}$ and direct correlations between $\mathcal{K}_{2ss}$ and $\mathcal{K}_{2cc,4s}$, pointing to destructive helicity interference and a possible CP-violating phase, while the $(C_{S_L},C_{S_R})$ scenario displays complementary behavior consistent with CP-conserving dynamics. These results establish baryonic semileptonic decays as a powerful and independent probe of the $R_{\tau/(\mu,e)}(D^{(*)})$ anomalies, with future measurements providing critical tests of the underlying NP structure.\\[5mm]
\noindent\textit{Keywords:} $B$-physics anomalies, Lepton Flavor Universality Violation, Semileptonic baryon decays, New Physics, Angular observables


\end{abstract}

%\date{\today}
\maketitle

\section{Introduction}\label{sec1}
The semileptonic and leptonic decays of hadrons containing a $b$ quark play a central role in the determination of the elements of the Cabibbo--Kobayashi--Maskawa (CKM) matrix. In this context, studies of flavor-changing charged-current (FCCC) and flavor-changing neutral-current (FCNC) transitions of $b-$hadrons are of particular importance. Among these, FCNC transitions are especially sensitive to effects of physics beyond the Standard Model (SM), as they are forbidden at tree level in the SM and occur only through loop- or box-level diagrams, where contributions from heavy virtual particles may enter.

Despite the analysis of Run-3 data from the Large Hadron Collider (LHC), collected at a center-of-mass energy of $13.6~\text{TeV}$ with an integrated luminosity of $39.7~\text{fb}^{-1}$, no direct evidence for new particles has been observed so far. Nevertheless, indirect indications of physics beyond the SM arise from phenomena such as neutrino oscillations and persistent anomalies in flavor observables, which suggest the existence of new physics (NP) \cite{Arbey:2021gdg,Gonzalez-Garcia:2022pbf}. Under these circumstances, FCNC decays provide a powerful probe for testing the SM and searching for NP effects. In particular, the exclusive decay modes
$B^{\pm}\!\to K^{(*)\pm}\ell^{+}\ell^{-}$,
$B^{0}\!\to K^{0}\ell^{+}\ell^{-}$, and
$B_s^{0}\!\to \phi\,\ell^{+}\ell^{-}$,
with $\ell=e,\mu$, have been extensively studied experimentally \cite{LHCb:2014cxe,LHCb:2014auh,LHCb:2015wdu,LHCb:2015svh,LHCb:2016ykl,LHCb:2021zwz,LHCb:2021xxq}.
Of particular interest are measurements of lepton-flavor universality violation (LFUV) in $B\to K^{(*)}\ell^{+}\ell^{-}$ decays \cite{LHCb:2022vje,LHCb:2022qnv,Smith:2024xgo,CMS:2024syx}, for which the dependence on CKM matrix elements and the associated hadronic form-factor uncertainties largely cancel. These observables have therefore been widely analyzed within various NP scenarios; see, \textit{e.g.}, Refs.~\cite{Celis:2017doq,Buttazzo:2017ixm,Aebischer:2019mlg,Alasfar:2020mne,Isidori:2021tzd,Ciuchini:2022wbq}. Recent experimental results indicate that these measurements are consistent with the SM predictions within approximately $0.2\sigma$ \cite{Hiller:2003js,Bordone:2016gaq,Mishra:2020orb,Isidori:2020acz,Bernlochner:2021vlv,Fischer:2021sqw,London:2021lfn,Crivellin:2021sff,Crivellin:2022qcj}.


Unlike FCNC transitions, the signatures of NP in semileptonic FCCC transitions $b\rightarrow c\ell\nu_{\ell}$ ($\ell=e,\mu,\tau$) are not diminished, where the measured values of the lepton flavor universality (LFU) ratio in $B\to D^{(*)}$ decays, \textit{i.e.}, $R_{\tau/\mu,e}\left(D^{(*)}\right)\equiv\mathcal{B}\left(B\rightarrow D^{(*)}\tau^-\overline{\nu}_{\tau}\right)/\mathcal{B}\left(B\rightarrow D^{(*)}\ell^-\bar{\nu}_{\ell}\right)$, with $\ell = e,\mu$, by BABAR \cite{BaBar:2012obs,BaBar:2013mob}, Belle \cite{Belle:2015qfa,Belle:2019rba,Belle:leptonphoton}
and LHCb \cite{LHCb:2015gmp,LHCb:2017smo,LHCb:2017rln,LHCb:2023zxo,LHCb:2023uiv}
deviate from their SM predictions. Recently, the
 Heavy Flavor Averaging Group (HFLAV), took averages of almost ten years data of all these experiments and showed $3.8\sigma$ combined deviation from the SM results  \cite{MILC:2015uhg, Na:2015kha, Aoki:2016frl, Fajfer:2012vx, Bigi:2016mdz, Bernlochner:2017jka, Bigi:2017jbd, Jaiswal:2017rve, Gambino:2019sif, Bordone:2019vic, Martinelli:2021onb, HFLAV:2024link, HFLAV:2025link}. Their most up-to-date averaged results reported by HFLAV group in 2025 \cite{HFLAV:2025link}, and the corresponding SM predictions are:
 \begin{eqnarray}
 R_{\tau/\mu,e}\left(D\right) &=& 0.347\pm0.025\;, \quad\quad R_{\tau/\mu,e}\left(D^*\right) = 0.288\pm 0.012\;, \label{HFLAV-RDDs}\\
R^{\text{SM}}_{\tau/\mu,e}\left(D\right)&=& 0.296\pm 0.004\;,\quad\quad R^{\text{SM}}_{\tau/\mu,e}\left(D^*\right) = 0.254\pm 0.005\;. \label{SM-RDDs} 
\end{eqnarray}
Governed by the same quark level FCCC transitions, the LFU ratio in $R_{\tau/\mu}^{LHCb}\left(J/\psi\right)$ and $R_{\tau/\mu}^{CMS2023, 2024}\left(J/\psi\right)$ are measured by the the LHCb \cite{LHCb:2017vlu} and CMS \cite{RJSi:CMS2023, RJSi:CMS2024} collaborations in $B_c \to J/\psi \ell \nu_\ell$ decays. Also, the $R_{\tau/\ell}\left(\Lambda_{c}\right)$ is measured by LHCb collaboration \cite{LHCb:2022piu} in $\Lambda_b \to \Lambda_c \tau^- \bar{\nu}_{\tau}$ decay and the naive average of $ R_{\tau/\mu}\left(J/\psi\right)$ and corresponding result for $R_{\tau/\ell}\left(\Lambda_{c}\right)$ are
\begin{equation}
 R_{\tau/\mu}\left(J/\psi\right) = 0.61\pm 0.18\;,\quad\quad  R_{\tau/\ell}\left(\Lambda_{c}\right) =  0.242 \pm 0.076\;.\label{Exp-RJpsiLC}
\end{equation}
These experimental results differ from the corresponding SM predictions
\begin{eqnarray}
 R^{\text{SM}}_{\tau/\mu}\left(J/\psi\right) &=&   0.258 \pm 0.038,\; \cite{Watanabe:2017mip, Harrison:2020nrv} \label{SN-RJPsi}\\
R^{\text{SM}}_{\tau/\ell}\left(\Lambda_c\right) &=& 0.324\pm0.004,\; \cite{Detmold:2015aaa, Bernlochner:2018kxh} \label{Exp-Lambdac}
\end{eqnarray}
by $1.9\sigma$ and $1.1\sigma$, respectively. In the case $R_{\tau/\mu}\left(J/\psi\right)$, the only shortcoming is the uncertainty in the measurement of the lifetime of $B_c$ meson because the pure leptonic decay $B_c \to \tau \nu_\tau$ is not measured yet \cite{Celis:2016azn, Alonso:2016oyd}. To take care of it, an upper limit of
$60\%, 30\%$, and $10\%$ on its branching ratio is imposed in the literature \cite{Gershtein:1994jw,Bigi:1995fs,Beneke:1996xe,Chang:2000ac,Kiselev:2000pp,Akeroyd:2017mhr}. 

In addition to the deviations observed in the LFU ratios, polarization observables in
$B \to D^{*}\tau\nu_{\tau}$ decays also provide important tests of the SM.
In particular, the longitudinal polarization asymmetry of the $\tau^{-}$ lepton,
$P_{\tau}(D^{*})$, and the longitudinal polarization fraction of the $D^{*}$ meson,
$F_{L}(D^{*})$, measured by the Belle collaboration
\cite{Belle:2017ilt,Belle:2016dyj,Belle:2019ewo},
exhibit deviations at the level of approximately $1.5\sigma$ from the corresponding SM
predictions \cite{Alok:2016qyh,Iguro:2020cpg}.
For $F_{L}(D^{*})$, the LHCb collaboration has reported results obtained by combining the
Run~1 data set with a subset of Run~2 data, covering the full kinematic range in $q^{2}$
\cite{LHCb:2023ssl,Chen:2024zot}.
Combining the Belle and LHCb measurements yields \cite{Iguro:2024hyk}
\begin{equation}
F_{L}(D^{*}) = 0.49 \pm 0.05\;, \label{FLDs}
\end{equation}
which is consistent with the SM prediction within $1\sigma$.

Motivated by these anomalies, numerous studies have explored possible NP
interpretations; see, \textit{e.g.},
Refs.~\cite{Azizi:2018axf,Azizi:2019aaf,Blanke:2018yud,Blanke:2019qrx,Huang:2018nnq,
Alok:2019uqc,Sahoo:2019hbu,Shi:2019gxi,Bardhan:2019ljo,Fedele:2022iib,
Asadi:2019xrc,Murgui:2019czp,Mandal:2020htr,Cheung:2020sbq,Colangelo:2020vhu,
Arslan:2023wgk,Yasmeen:2024cki, Huang:2025kof, Tang:2022nqm}.
In many of these analyses, dimension-six operators involving only left-handed (LH)
neutrinos in $b \to c \tau \bar{\nu}_{\tau}$ transitions were considered.
More general scenarios, including right-handed (RH) neutrinos and/or RH quark currents
within the model-independent weak effective Hamiltonian (WEH), have also been investigated;
see, \textit{e.g.},
Refs.~\cite{Greljo:2018ogz,Azatov:2018kzb,Heeck:2018ntp,Babu:2018vrl,He:2017bft,
Gomez:2019xfw,Alguero:2020ukk,Dutta:2013qaa,Dutta:2017xmj,Dutta:2017wpq,
Dutta:2018jxz}.
By performing global fits to the available $b \to c \tau \bar{\nu}_{\tau}$ data,
constraints on the NP Wilson coefficients (WCs) $C_{O_i}$, with
$i = V_{L,R},\, S_{L,R},\, T$, were obtained in
Refs.~\cite{Freytsis:2015qca,Alok:2017qsi,Arslan:2025zph}.
Following updated data releases from Belle and LHCb, revised constraints based on the
2024 HFLAV averages \cite{HFLAV:2024link} and their implications for various FCCC decays
were presented in Ref.~\cite{Arslan:2025zph}.

In light of the evolving experimental situation, particularly the updated 2025 HFLAV
averages for $R_{\tau/\mu,e}(D)$, $R_{\tau/\mu,e}(D^{*})$, as well as the updated measurements of the observables
$F_{L}(D^{*})$, $P_{\tau}(D^{*})$, $R_{\tau/\ell}(\Lambda_{c})$, and
$R_{\tau/\mu}(J/\psi)$ (see
Eqs.~\eqref{Exp-RJpsiLC}–\eqref{FLDs}) \cite{HFLAV:2025link},
it is timely to revisit and update the theoretical analyses.
As a first step, following
Refs.~\cite{Alok:2017qsi,Arslan:2025zph}, we perform an updated global fit  within the framework of the
model-independent WEH, assuming left-handed neutrinos and real NP WCs,
and incorporating the latest constraints on
$R_{\tau/\mu,e}(D)$, $R_{\tau/\mu,e}(D^{*})$, $F_{L}(D^{*})$, and $P_{\tau}(D^{*})$.

The baryonic decay $\Lambda^0_b \to \Lambda^+_c \tau^- \bar{\nu}_{\tau}$ is currently consistent
with SM expectations within experimental uncertainties.
Nevertheless, a potential window for NP effects remains, particularly toward the lower
end of the experimentally allowed ranges.
Unlike the mesonic transitions $B \to D$ and $B \to D^{*}$, both the initial and final
states in the baryonic decay, $\Lambda_b$ and $\Lambda_c$, carry spin-$\tfrac{1}{2}$.
As a result, all effective operators contribute to the decay
$\Lambda_b^0 \to \Lambda_c^+ \tau^- \bar{\nu}_{\tau}$.
These baryonic transitions exhibit kinematic structures and form-factor dependencies
distinct from their mesonic counterparts, thereby providing complementary sensitivity to
the underlying $b \to c \tau \bar{\nu}_{\tau}$ dynamics.
The primary limitation arises from the comparatively less precise knowledge of the
$\Lambda_b \to \Lambda_c$ form factors relative to those in $B \to (D,D^{*})$ decays.

The decay $\Lambda^0_b \to \Lambda_c \tau^- \bar{\nu}_{\tau}$ has been studied extensively
within the SM and in a variety of NP scenarios, together with dedicated calculations of
the relevant form factors; see, \textit{e.g.},
Refs.~\cite{Detmold:2015aaa,Azizi:2018axf,Bernlochner:2018kxh,Gutsche:2015rrt,
Gutsche:2015mxa,Shivashankara:2015cta,Dutta:2015ueb,Faustov:2016pal,
Li:2016pdv,Celis:2016azn,Datta:2017aue}.
An angular analysis of the cascade decay
$\Lambda_b^0 \to \Lambda_c^+(\to \Lambda^0 \pi^+) \tau^- \bar{\nu}_{\tau}$
requires knowledge of the polar and azimuthal angles of the $\tau^-$ lepton
\cite{Gutsche:2015mxa,Shivashankara:2015cta,Dutta:2015ueb,Faustov:2016pal,
Li:2016pdv,Celis:2016azn,Datta:2017aue}.
Since the $\tau^-$ is accompanied by an undetected neutrino, these angles cannot be
reconstructed precisely, rendering the corresponding angular distributions inaccessible
experimentally \cite{Bhattacharya:2020lfm}.
A viable alternative is to consider the subsequent decay
$\tau^- \to \pi^- \nu_{\tau}$, leading to the full cascade process $
\Lambda_b^0 \to \Lambda_c^+(\to \Lambda^0 \pi^+)\,
\tau^-(\to \pi^- \nu_{\tau})\,\bar{\nu}_{\tau}
$.
This channel has been analyzed assuming an unpolarized $\Lambda_b$ initial state and
including all possible Lorentz structures of the NP effective operators in \cite{Hu:2020axt}.
In this case, the three-momenta of the final-state particles
$\Lambda^0$, $\pi^+$, and $\pi^-$ are experimentally accessible.
After integrating over the relevant kinematic and angular variables, several observables,
such as the $\Lambda_c$ polarization $P_{\Lambda_c}(q^2)$ and the forward--backward
asymmetry of the $\pi^-$, $A_{FB}(q^2)$, can be extracted.



In this work, we employ the latest form factors for the
$\Lambda_b \to \Lambda_c$ transition calculated using lattice QCD
\cite{Bernlochner:2018kxh} and perform a detailed analysis of the angular
structure of the five-fold differential decay
$\Lambda_b^0 \to \Lambda_c^+(\to \Lambda^0 \pi^+)\,
\tau^-(\to \pi^- \nu_\tau)\bar{\nu}_\tau$ within the framework of the
model-independent WEH, assuming left-handed neutrinos.
In particular, we study the full set of angular coefficients
$\mathcal{K}_i$, which are linearly related to the helicity amplitudes
and therefore provide a cleaner separation of possible new-physics (NP)
effects compared to inclusive observables such as the LFU ratio
$R_{\tau/\ell}(\Lambda_{c})$.
To quantify the impact of NP in this decay, we use the allowed NP
parameter space obtained from constraints on
$R_{\tau/\mu,e}(D)$, $R_{\tau/\mu,e}(D^{*})$, $F_{L}(D^{*})$, and $P_{\tau}(D^{*})$ using latest HFLAV averages
\cite{HFLAV:2025link} and compare our results with the corresponding
SM predictions and available experimental measurements.
We find that NP scenarios capable of explaining the anomalies observed in
$\bar{B} \to D^{(*)}\tau^- \bar{\nu}_\tau$ decays can also induce sizable
effects in several observables of the baryonic decay
$\Lambda_b^0 \to \Lambda_c^+(\to \Lambda^0 \pi^+)\,
\tau^-(\to \pi^- \nu_\tau)\bar{\nu}_\tau$.

The main benchmarks of the present analysis are summarized as follows:
\begin{itemize}
    \item We incorporate the HFLAV Spring~2025 averages for
    $R_{\tau/\mu,e}(D^{(*)})$, which indicate an overall discrepancy of
    approximately $3.8\sigma$ from the SM, with a correlation coefficient
    of $-0.39$.
    \item We include constraints from the branching ratio
    $\mathcal{B}(B_c \to \tau \bar{\nu}_\tau)$, imposing upper bounds of
    $60\%$, $30\%$, and $10\%$, together with current LHC collider limits
    based on $\tau^\pm\nu_\tau$ searches at an integrated luminosity of
    $139~\mathrm{fb}^{-1}$, evaluated at the scale $\mu = m_b$.
    \item In contrast to earlier studies favoring the
    $(C_{V_L},C_{S_R})$ and $(C_{V_L},C_{S_L}=-4C_T)$ solutions with high
    $p$-values (approximately $87\%$ and $85\%$) and a strong
    $\sim4.2\sigma$ pull from the SM, our updated analysis reveals a
    distinct NP preference driven by $(\Re[C_{S_L}=4C_T],\Im[C_{S_L}=4C_T])$
    interactions.
    \item We demonstrate that the angular coefficients
    $\mathcal{K}_{1c}$, $\mathcal{K}_{2ss}$, $\mathcal{K}_{2cc}$, and
    $\mathcal{K}_{4s}$ are the most sensitive to NP effects, providing a
    novel strategy to identify helicity-driven signatures of physics
    beyond the SM.
    \item We find that the observed direct--inverse correlation patterns
    between real $(C_{S_L},C_{S_R})$ and complex
    $(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T])$ NP scenarios
    offer a distinctive diagnostic tool for disentangling different NP
    contributions.
    \item We highlight that baryonic angular correlations, in contrast to
    mesonic ones, exhibit rich interference patterns that allow for the
    isolation of both CP-conserving and CP-violating effects.
\end{itemize}

The paper is organized as follows.
In Sec.~\ref{sec2}, we introduce the WEH,
including the SM operators and possible NP vector, scalar, and tensor
interactions.
For completeness, analytic expressions for $R_{\tau/\mu,e}(D^{(*)})$, $P_\tau(D^{(*)})$, and $F_L(D^*)$,
expressed in terms
of the NP Wilson coefficients, are collected in
Appendix~\ref{AppendixA}.
In Sec.~\ref{subsec3}, we perform a global fit to the latest experimental
data to determine the allowed parameter space for NP Wilson
coefficients, ignoring the constraints from
$\mathcal{B}(B_c \to \tau \bar{\nu}_\tau)$ to maximize the fit sensitivity.
Section~\ref{secIII} presents the transversality amplitudes and angular
coefficients for the decay
$\Lambda_b^0 \to \Lambda_c^+(\to \Lambda^0 \pi^+)\,
\tau^-(\to \pi^- \nu_\tau)\bar{\nu}_\tau$, together with the five-fold
differential decay distribution and related observables.
A phenomenological analysis based on lattice-QCD form factors is discussed in Sec.~\ref{Num-anlaysis}. The
correlations among the various observables are discussed in
Sec.~\ref{correlation}, and our conclusions are summarized in
Sec.~\ref{sec6}.
Additional technical details concerning
derivation of the five-fold $\Lambda_b^0 \to \Lambda_c^+(\to \Lambda^0 \pi^+)\,
\tau^-(\to \pi^- \nu_\tau)\bar{\nu}_\tau$ decay
observables in terms of helicity amplitudes are provided in Appendix \ref{obsRLc}.




\section{Theoretical Framework and Bounds on the NP parameter space}\label{sec2}
\subsection{Standard Model Effective Hamiltonian (SMEH)}

We consider the dimension-six semileptonic operators contributing at tree level to the WEH for the transition
$b \to c \tau^- \bar{\nu}_\tau$. Matching these operators onto the Standard Model Effective Field Theory (SMEFT) yields the relations among the corresponding
WCs. The most general WEH for $b \to c \tau^- \bar{\nu}_\tau$, including all Lorentz-invariant structures, is given by
\cite{Freytsis:2015qca,Alok:2017qsi}
\begin{equation}
H_{\text{eff}}
=\frac{4G_{F}V_{cb}}{\sqrt{2}}
\left[
\left(C_{V_{L}}\right)_{\text{SM}}\mathcal{O}_{V_{L}}
+\frac{\sqrt{2}}{4G_{F}V_{cb}}\frac{1}{\Lambda^{2}}
\sum_{i} C_{i}\mathcal{O}_{i}
\right],
\label{weh}
\end{equation}
where $G_{F}$ is the Fermi constant, $V_{cb}$ the CKM matrix element, and
$P_{R,L}=(1\pm\gamma_{5})/2$ are the chiral projectors. The SM contribution is normalized to
$(C_{V_{L}})_{\text{SM}}=0$.
The NP operators $\mathcal{O}_{i}$ with
$i=V_{L},V_{R},S_{L},S_{R},T$ are \cite{Buchmuller:1985jz,Grzadkowski:2010es,Aebischer:2015fzz}
\begin{align}
\mathcal{O}_{V_{L}} &= (\bar{c}\gamma^{\mu}P_{L}b)(\bar{\tau}\gamma_{\mu}P_{L}\nu), \qquad
\mathcal{O}_{V_{R}} = (\bar{c}\gamma^{\mu}P_{R}b)(\bar{\tau}\gamma_{\mu}P_{L}\nu), \nonumber \\
\mathcal{O}_{S_{L}} &= (\bar{c}P_{L}b)(\bar{\tau}P_{L}\nu), \qquad\qquad
\mathcal{O}_{S_{R}} = (\bar{c}P_{R}b)(\bar{\tau}P_{L}\nu), \nonumber \\
\mathcal{O}_{T} &= (\bar{c}\sigma^{\mu\nu}P_{L}b)(\bar{\tau}\sigma_{\mu\nu}P_{L}\nu).
\label{eq2}
\end{align}

The relevant low-energy scale for $b \to c \tau \bar{\nu}$ transitions is
$\mu_{b}=m_{b}$. The WCs at $\mu_{b}$ are related to those at the NP scale
$\Lambda=2~\text{TeV}$ through renormalization-group evolution
\cite{Gonzalez-Alonso:2017iyc,Blanke:2018yud}:
\begin{align}
\widetilde{C}_{V_{L}}(m_{b}) &= 1.12\,C_{V_{L}}^{\text{eff}}(2~\text{TeV}), \qquad
\widetilde{C}_{V_{R}}(m_{b}) = 1.07\,C_{V_{R}}^{\text{eff}}(2~\text{TeV}), \nonumber \\
\widetilde{C}_{S_{R}}(m_{b}) &= 2\,C_{S_{R}}^{\text{eff}}(2~\text{TeV}), \nonumber \\
\begin{pmatrix}
\widetilde{C}_{S_{L}}(m_{b}) \\
\widetilde{C}_{T}(m_{b})
\end{pmatrix}
&=
\begin{pmatrix}
1.91 & 0 \\
-0.38 & 0.89
\end{pmatrix}
\begin{pmatrix}
C_{S_{L}}^{\text{eff}}(2~\text{TeV}) \\
C_{T}^{\text{eff}}(2~\text{TeV})
\end{pmatrix}.
\label{eq3}
\end{align}
For the WEH in Eq.~(\ref{weh}), the physical observables considered in this work can be
expressed in terms of the NP WCs evaluated at $\mu_{b}=m_{b}$. Their explicit expressions are
available in Refs.~\cite{Watanabe:2017mip,Iguro:2018vqb,Asadi:2018wea,Asadi:2018sym,
Ligeti:2016npd,Robinson:2018gza,Gomez:2019xfw,Cardozo:2020uol,Fedele:2022iib,
Mandal:2020htr,Kamali:2018bdp,Iguro:2022yzr} and are summarized in
Appendix~\ref{AppendixA}.


\subsection{Analysis of the parameter space of NP WCs using only $B$ meson data}\label{subsec3}

In this section, we explore the parameter space of NP WCs using the most recent HFLAV data on FCCC transitions \cite{HFLAV:2025link}. To this end, we employ the fitting strategy developed in Ref.~\cite{Blanke:2018yud} and implemented in Ref.~\cite{Arslan:2025zph}. The analysis assumes all NP WCs are strictly imaginary to maximize CP violation.

Our global fit incorporates four observables,
\[
N_{\text{obs}}=4:\qquad
R_{\tau/\mu,e}(D),\;
R_{\tau/{\mu,e}}(D^{*}),\;
P_{\tau}(D^{*}),\;
F_{L}(D^{*}),
\]
and is performed under two scenarios:  
(i) a one-dimensional (1D) fit, where only one NP WC is switched on at a time, and  
(ii) a two-dimensional (2D) fit, where two NP WCs are allowed to be nonzero simultaneously. Accordingly, the number of fit parameters is $N_{\text{par}}=1\,(2)$ for the 1D (2D) case, yielding the number of degrees of freedom
\[
N_{\text{dof}} = N_{\text{obs}} + N_{\text{par}} = 5\,(6).
\]

Within this framework, we determine the best-fit points (BFPs), their $1\sigma$ and $2\sigma$ ranges, the minimum $\chi^2$, the corresponding $p$-values, and the SM pull for all 1D scenarios. These results are summarized in Table~\ref{1d-table}. The effects
$\mathcal{B}(B_c^- \to \tau^- \bar{\nu}_\tau) < 0.1\%,\,0.3\%,\,0.6\%$
constraints are consistently included in the fits.

From Table~\ref{1d-table}, we observe that the fit strongly prefers the SM, yielding an excellent $p$-value of about $93\%$, corresponding to an approximately $0\sigma$ pull from the SM. Pure scalar scenarios involving $C_{S_L}$ or $C_{S_R}$ are strictly excluded by the data. In contrast, the relation $C_{S_L}=4C_T$ is the best-fit scenario.

For the two-dimensional fits, the corresponding BFPs, $\chi^2_{\text{min}}$, $p$-values, and SM pulls are listed in Table~\ref{2d-table-1}, while their $1\sigma$ and $2\sigma$ allowed regions are shown in Fig.~\ref{s2d-fig}. The orange contours represent parameter regions unconstrained by $\mathcal{B}(B_c^- \to \tau^- \bar{\nu}_\tau)$, whereas the red and green contours illustrate the impact of the $60\%$ and $10\%$ branching-ratio bounds, respectively. The light- and dark-gray bands denote the regions allowed by the $10\%$ and $60\%$ constraints, and any point lying outside these bands is considered excluded.

Among the 2D scenarios, the $(C_{V_L},C_{S_R})$ and $(C_{V_L},C_{S_L}=-4C_T)$ solutions provide the best description of the data, with very high $p$-values of approximately $87\%$ and $85\%$, respectively, corresponding to a strong $\sim4.2\sigma$ pull from the SM. The scenario with $C_{S_L}=4C_T$ remains allowed but is clearly less favored, particularly under the stringent constraint
$\mathcal{B}(B_c^- \to \tau^- \bar{\nu}_\tau)<10\%$, where the fit quality deteriorates significantly, yielding a $p$-value of about $22\%$. The pure scalar combination $(C_{S_L},C_{S_R})$ remains viable for relaxed branching-ratio bounds ($<60\%$), but its preference decreases sharply as the constraint tightens, resulting in a $p$-value of only $\sim13\%$ for the $<10\%$ case, which
indicates an increasing tension with the data. 

\begin{table}[H]
\centering{}%
\renewcommand{\arraystretch}{1.1}
\begin{tabular}{|c|c|c|c|c|c|c|}
\toprule 
\multicolumn{7}{c}{( $\chi_{\text{SM}}^{2}=15.12$, $p-\text{value}=4.46\times10^{-3}$
)}\tabularnewline
\midrule
\midrule 
\hline\hline
WC & BFP & $\chi_{\text{min}}^{2}$ & $p-\text{value}$ $\%$ & $\text{pull}_{\text{SM}}$ & $1\sigma$-range & $2\sigma$-range\tabularnewline
\hline
\midrule
\midrule 
$C_{V_{L}}$ & $0.06$ & $0.43$ & $93.36$ & $4.19$ & $\left[0.04,0.09\right]$ & $\left[0.02,0.10\right]$\tabularnewline
 \hline
\midrule 
$C_{S_{R}}$ & $0.08$ & $5.24$ & $15.54$ & $3.58$ & $\left[0.04,0.12\right]$ & $\left[0.02,0.14\right]$\tabularnewline
 \hline
\midrule 
$C_{S_{L}}$ & $0.08$ & $9.19$ & $2.69$ & $2.97$ & $\left[0.03,0.12\right]$ & $\left[0.01,0.14\right]$\tabularnewline
 \hline
\midrule 
$C_{S_{L}}=4C_{T}$ & $0.02$ & $17.73$ & $0.05$ & $0.54$ & $\left[-0.04,0.07\right]$ & $\left[-0.08,0.10\right]$\tabularnewline
 \hline\hline
\bottomrule
\end{tabular}
\caption{\label{1d-table}
Results of the one-dimensional fits for real NP WCs. 
Shown are the BFPs, the minimum $\chi^2$, the $p$-value (in \%), the SM pull, and the corresponding $1\sigma$ and $2\sigma$ ranges of the WCs. 
The fits are performed under the constraints 
$\mathcal{B}(B_c^- \to \tau^- \bar{\nu}_\tau) < 60\%,\,30\%$, and $10$. 
We find that the results are insensitive to the choice among these three branching-ratio limits.
}
\end{table}

\begin{figure}[H]
\centering{} \subfloat[]{\includegraphics[width=6cm, height=5cm]{sc.pdf}}\quad \subfloat[]{\includegraphics[width=6cm, height=5cm]{sa.pdf}} 
\centering{} \subfloat[]{\includegraphics[width=6cm, height=5cm]{sd.pdf}}\quad \subfloat[]{\includegraphics[width=6cm, height=5cm]{sb.pdf}}
%[width=4.5cm, height=4.2cm]

\caption{\label{s2d-fig}
Results of the fits for NP scenarios at the scale $\mu = 2\,\text{TeV}$. 
The light- and dark-gray shaded regions indicate the constraints 
$\mathcal{B}(B_c^- \to \tau^- \bar{\nu}_\tau) < 10\%$ and $< 60\%$, respectively. 
The light (dark) contours correspond to the $1\sigma$ ($2\sigma$) regions around the BFP, shown in black. 
In panels (a) and (b), the orange regions are unaffected by either branching-ratio constraint, while in panels (c) and (d) the red and green regions represent the $60\%$ and $10\%$ constraints, respectively. 
The purple-shaded area outside the dashed ellipse denotes the region excluded by collider bounds at an integrated luminosity of $139\,\text{fb}^{-1}$.
}
\end{figure}

\begin{table}[H]
\centering{}%
\renewcommand{\arraystretch}{1.35}
\begin{tabular}{|c|c|c|c|c|c|}
\toprule 
\multicolumn{6}{c}{( $\chi_{\text{SM}}^{2}=15.12$, $p-\text{value}=4.46\times10^{-3}$
)}\tabularnewline
\hline 
WC & BR & BFP & $\chi_{min}^{2}$ & $p-value$ $\%$ & $pull_{SM}$\tabularnewline
\hline 
\hline 
$\left(C_{V_{L}},C_{S_{R}}\right)$ & - & $\left(0.06,0.01\right)$ & $0.28$ & $86.99$ & $4.21$\tabularnewline
\hline 
$\left(C_{V_{L}},C_{S_{L}}=-4C_{T}\right)$ & - & $\left(0.06,0.01\right)$ & \multirow{1}{*}{$0.32$} & \multirow{1}{*}{$85.04$} & \multirow{1}{*}{$4.21$}\tabularnewline
\hline 
\multirow{2}{*}{$\left(\Re\left[C_{S_{L}}=4C_{T}\right],\Im\left[C_{S_{L}}=4C_{T}\right]\right)$} & $\begin{array}{c}
<60\%\\
\&30\%
\end{array}$ & $\left(-0.04,-0.29\right)$ & $0.53$ & $76.63$ & $4.18$\tabularnewline
\cline{2-6} \cline{3-6} \cline{4-6} \cline{5-6} \cline{6-6} 
 & $<10\%$ & $\left(-0.01,-0.23\right)$ & $3.01$ & $22.19$ & $3.87$\tabularnewline
\hline 
\multirow{3}{*}{$\left(C_{S_{L}},C_{S_{R}}\right)$} & $<60\%$ & $\left(-0.19,0.24\right)$ & $0.54$ & $76.25$ & $4.18$\tabularnewline
\cline{2-6} \cline{3-6} \cline{4-6} \cline{5-6} \cline{6-6} 
 & $<30\%$ & $\left(-0.71,0.98\right)$ & $0.84$ & $65.62$ & $3.78$\tabularnewline
\cline{2-6} \cline{3-6} \cline{4-6} \cline{5-6} \cline{6-6} 
 & $<10\%$ & $\left(-0.03,0.10\right)$ & $4.06$ & $13.15$ & $3.74$\tabularnewline
\hline 
\end{tabular}\caption{\label{2d-table-1} The results of the two-dimensional fit for NP WCs, including BFP, $\chi_{\text{min}}^{2}$,\; $p-\text{value}$ $\%$,\; and $\text{pull}_{\text{SM}}$,\; of the corresponding WCs. These numbers are obtained by incorporating bounds on $\mathcal{B}\left(B_{c}^{-}\to\tau^{-}\bar{\nu}_{\tau}\right) <60\%,\;30\%,\;10\%$
for set of observables.}
\end{table}

We emphasize that our results are in agreement with Ref.~\cite{Blanke:2018yud} for the one-dimensional scenario, where only the $C_{V_L}$ operator provides the best fit ($p \simeq 93\%$, corresponding to an approximately $4\sigma$ pull from the SM). 
The scalar solutions are less favored, and the $C_{S_L}=4C_T$ scenario is strongly disfavored, confirming the suppression of scalar–tensor NP contributions. 

In contrast, for the two-dimensional fits, our conclusions differ from those of Ref.~\cite{Blanke:2018yud}. 
While the $(C_{S_L},C_{S_R})$ scenario was found to yield the highest $p$-value in that study, our analysis identifies it as the least favored among the two-parameter solutions. 
Instead, the $(C_{V_L},C_{S_R})$ and $(C_{V_L},C_{S_L}=-4C_T)$ scenarios provide the best fits, with $p$-values exceeding $85\%$ and an approximately $4\sigma$ pull from the SM. 
This inversion indicates that the updated dataset and the treatment of observables in our analysis strongly favor correlated vector–scalar or vector–tensor NP scenarios over purely scalar combinations.

Consequently, in the following sections, we focus our phenomenological discussion on the NP scenarios satisfying $\chi^2_{\mathrm{min}} \leq 1$.


\subsection{Impact of collider (LHC) bounds}\label{subcolb}
The current collider bounds on the NP WCs, based on the $\tau^{\pm}\nu$ search at $\mu=m_b$ with an integrated luminosity of $139\;\text{fb}^{-1}$, and the projected bounds for the HL-LHC with $1000\,(3000)\;\text{fb}^{-1}$, are \cite{Greljo:2018tzh, Faroughy:2016osc, Iguro:2018fni, Endo:2021lhi}:
\begin{equation}
\left|\widetilde{C}_{V_{L}}\right|<0.30\,(0.14),\quad
\left|\widetilde{C}_{V_{R}}\right|<0.32\,(0.15),\quad
\left|\widetilde{C}_{S_{L,R}}\right|<0.55\,(0.25),\quad
\left|\widetilde{C}_{T}\right|<0.15\,(0.07).
\end{equation}

Applying these bounds to various combinations of NP WCs, we illustrate their impact on the allowed parameter space with the purple-shaded ellipse in Fig.~\ref{s2d-fig}. 
In particular, the combinations $\left(\Re\!\left[C_{S_{L}}=4C_{T}\right], \Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ and $(C_{S_{L}}, C_{S_{R}})$ are now subject to stringent constraints, as the lower portion of the previously allowed region \cite{Hu:2020axt} is excluded. 
Furthermore, when imposing a $60\%$ branching ratio constraint, the regions corresponding to the BFPs are also excluded, resulting in a substantial reduction of the viable parameter space. 
In contrast, all other benchmark scenarios remain consistent with the current collider limits.



\section{Five-fold $\Lambda_b^0 \to \Lambda_c^+(\to \Lambda^0 \pi^+) \tau^-(\to \pi^- \nu_\tau)\bar{\nu}_\tau$ decay distribution and angular observables}
\label{secIII}

In this section, we present the analytical expressions for the angular
distribution of the decay
$\Lambda_b^0 \to \Lambda_c^+(\to \Lambda^0 \pi^+) \tau^-(\to \pi^- \nu_\tau)\bar{\nu}_\tau$.
The details of the calculation and the conventions adopted are provided
in Appendix~\ref{AppendixA}.

\subsection{Transversity amplitudes}

As an exclusive decay, the hadronic matrix elements of the vector and
axial-vector currents governing the $\Lambda_b \to \Lambda_c$ transition
can be parameterized in terms of six helicity form factors,
$F_{+}$, $F_{\perp}$, $F_{0}$, $G_{+}$, $G_{\perp}$, and $G_{0}$
\cite{Datta:2017aue}.
Using Ward identities for the $\Lambda_b \to \Lambda_c$ matrix elements,
the scalar and pseudoscalar current contributions can be expressed in
terms of $F_{0}$ and $G_{0}$, respectively. We used the numerical values of these form factors along with their different fit parameters from \cite{Detmold:2015aaa,Datta:2017aue}. 

In the absence of tensor operators, six independent transversity
amplitudes can be defined as \cite{Hu:2020axt}:
\begin{align}
\mathcal{A}_{\perp t} &=
\mathcal{A}_{\perp t}^{SP}
+ \frac{m_\tau}{\sqrt{q^{2}}}\,
\mathcal{A}_{\perp t}^{VA},
&
\mathcal{A}_{\parallel t} &=
\mathcal{A}_{\parallel t}^{SP}
+ \frac{m_\tau}{\sqrt{q^{2}}}\,
\mathcal{A}_{\parallel t}^{VA},\label{eq:11}
\\
\mathcal{A}_{\perp 1} &=
-2 F_{\perp}\sqrt{Q_{-}}
\left(1+C_{V_L}+C_{V_R}\right),
&
\mathcal{A}_{\parallel 1} &=
-2 G_{\perp}\sqrt{Q_{+}}
\left(-1-C_{V_L}+C_{V_R}\right),\label{eq:12}
\\
\mathcal{A}_{\perp 0} &=
F_{+}\sqrt{2Q_{-}}
\frac{m_1+m_2}{\sqrt{q^{2}}}
\left(1+C_{V_L}+C_{V_R}\right),
&
\mathcal{A}_{\parallel 0} &=
G_{+}\sqrt{2Q_{+}}
\frac{m_1-m_2}{\sqrt{q^{2}}}
\left(-1-C_{V_L}+C_{V_R}\right).\label{eq:13}
\end{align}
Here, $\perp$ and $\parallel$ denote the two transversity states.
The subscript $t$ corresponds to the time-like polarization of
the off-shell $\tau^-\bar{\nu}_\tau$ system, while the subscripts
$1$ and $0$ indicate the magnitude of the $z$-component of the total
angular momentum of the $\tau^-\bar{\nu}_\tau$ pair.
The kinematic factors are defined as
$Q_{\pm} = (m_1 \pm m_2)^2 - q^2$.

The time-like transversity amplitudes are given by
\begin{align}
\mathcal{A}_{\perp t}^{SP} &=
F_{0}\sqrt{2Q_{+}}
\frac{m_1-m_2}{m_b-m_c}
\left(C_{S_L}+C_{S_R}\right),\label{eq:14}
\\
\mathcal{A}_{\parallel t}^{SP} &=
- G_{0}\sqrt{2Q_{-}}
\frac{m_1+m_2}{m_b+m_c}
\left(-C_{S_L}+C_{S_R}\right),\label{eq:15}
\\
\mathcal{A}_{\perp t}^{VA} &=
F_{0}\sqrt{2Q_{+}}
\frac{m_1-m_2}{\sqrt{q^{2}}}
\left(1+C_{V_L}+C_{V_R}\right),\label{eq:16}
\\
\mathcal{A}_{\parallel t}^{VA} &=
G_{0}\sqrt{2Q_{-}}
\frac{m_1+m_2}{\sqrt{q^{2}}}
\left(-1-C_{V_L}+C_{V_R}\right).\label{eq:17}
\end{align}

When tensor operators are included, the matrix elements can be
parameterized by four additional helicity form factors,
$h_{+}$, $h_{\perp}$, $\tilde{h}_{+}$, and $\tilde{h}_{\perp}$.
This leads to four extra transversity amplitudes \cite{Hu:2020axt}:
\begin{align}
\mathcal{A}_{\perp 1}^{T} &=
4 h_{\perp}\sqrt{Q_{-}}
\frac{m_1+m_2}{\sqrt{q^{2}}} C_T,
&
\mathcal{A}_{\parallel 1}^{T} &=
4 \tilde{h}_{\perp}\sqrt{Q_{+}}
\frac{m_1-m_2}{\sqrt{q^{2}}} C_T,\label{eq:18}
\\
\mathcal{A}_{\perp 0}^{T} &=
-2 h_{+}\sqrt{2Q_{-}}\, C_T,
&
\mathcal{A}_{\parallel 0}^{T} &=
-2 \tilde{h}_{+}\sqrt{2Q_{+}}\, C_T.\label{eq:19}
\end{align}

The superscript $T$ indicates contributions arising exclusively from
tensor operators.

\subsection{Angular distribution}
The measurable angular distribution of the five-body decay
$\Lambda_{b}^{0}\to\Lambda_{c}^{+}(\to\Lambda^{0}\pi^{+})
\tau^{-}(\to\pi^{-}\nu_{\tau})\bar{\nu}_{\tau}$,
for an unpolarized $\Lambda_b^0$, is described by the invariant mass
squared of the $\tau^-\bar{\nu}_\tau$ system, $q^{2}$;
the helicity angle $\theta_{\Lambda}$ of the $\Lambda^{0}$ baryon in the
$\Lambda_{c}^{+}$ rest frame; and the energy $E_{\pi}$, polar angle
$\theta_{\pi}$, and azimuthal angle $\phi_{\pi}$ of the $\pi^{-}$ in the
$\tau^-\bar{\nu}_\tau$ center-of-mass frame.
The kinematic conventions are illustrated in Fig.~1 and detailed in
Appendix~A.

The five-fold differential decay rate can be written as
\begin{align}
\frac{d^{5}\Gamma}
{dq^{2}\, dE_{\pi}\, d\cos\theta_{\pi}\, d\phi_{\pi}\, d\cos\theta_{\Lambda}}
&=
\frac{G_{F}^{2}\,|V_{cb}|^{2}\,|q|\,(q^{2})^{3/2}\, m_{\tau}^{2}}
{2^{8}\pi^{4} m_{1}^{2}(m_{\tau}^{2}-m_{\pi}^{2})^{2}}
\nonumber\\
&\quad\times
\mathcal{B}(\Lambda_{c}\to\Lambda\pi^{+})\,
\mathcal{B}(\tau\to\pi^{-}\nu_{\tau})\,
\mathcal{K}(q^{2},E_{\pi},\cos\theta_{\Lambda},
\cos\theta_{\pi},\phi_{\pi}),
\end{align}
where $|\textbf{q}|=\sqrt{Q_{+}Q_{-}}/(2m_{1})$ is the magnitude of the
$\Lambda_{c}$ three-momentum in the $\Lambda_{b}$ rest frame, and
$m_{1}$ denotes the $\Lambda_{b}$ mass. In terms of angular coefficients, 
the angular function $\mathcal{K}$ can be expressed as \cite{Hu:2020axt}:
\begin{align}
\mathcal{K}
&=
\sum_{i=1}^{10}
\mathcal{K}_{i}(q^{2},E_{\pi})\,
\Omega_{i}(\cos\theta_{\Lambda},\cos\theta_{\pi},\phi_{\pi})
\nonumber\\
&=
\left(\mathcal{K}_{1ss}\sin^{2}\theta_{\pi}
+\mathcal{K}_{1cc}\cos^{2}\theta_{\pi}
+\mathcal{K}_{1c}\cos\theta_{\pi}\right)+
\left(\mathcal{K}_{2ss}\sin^{2}\theta_{\pi}
+\mathcal{K}_{2cc}\cos^{2}\theta_{\pi}
+\mathcal{K}_{2c}\cos\theta_{\pi}\right)\cos\theta_{\Lambda}
\nonumber\\
&\quad+
\left(\mathcal{K}_{3sc}\sin\theta_{\pi}\cos\theta_{\pi}
+\mathcal{K}_{3s}\sin\theta_{\pi}\right)
\sin\theta_{\Lambda}\sin\phi_{\pi}+
\left(\mathcal{K}_{4sc}\sin\theta_{\pi}\cos\theta_{\pi}
+\mathcal{K}_{4s}\sin\theta_{\pi}\right)
\sin\theta_{\Lambda}\cos\phi_{\pi}\;.
\end{align}

The ten angular observables $\mathcal{K}_{i}(q^{2},E_{\pi})$
can be written entirely in terms of the transversity amplitudes,
the dimensionless kinematic factors defined in
Eqs.~(\ref{eq:11})--(\ref{eq:19}).
Their explicit expressions are
\begin{align}
\mathcal{K}_{1ss} & =S_{t}\left|\mathcal{A}_{\perp t}\right|^{2}+\left(S_{1}-S_{3}\right)\left|\mathcal{A}_{\perp1}\right|^{2}+\left(S_{1}+S_{3}\right)\left|\mathcal{A}_{\perp0}\right|^{2}+\left(S_{1}^{T}-S_{3}^{T}\right)\left|\mathcal{A}_{\perp1}^{T}\right|^{2}+\left(S_{1}^{T}+S_{3}^{T}\right)\left|\mathcal{A}_{\perp0}^{T}\right|^{2}\notag\\
 & +\Re\left[\left(R_{1}-R_{3}\right)\mathcal{A}_{\perp1}\mathcal{A}_{\perp1}^{T*}+\left(R_{1}+R_{3}\right)\mathcal{A}_{\perp0}\mathcal{A}_{\perp0}^{T*}\right]+\left(\perp\leftrightarrow\parallel\right),\label{eq:22}\\
\mathcal{K}_{1cc} & =S_{t}\left|\mathcal{A}_{\perp t}\right|^{2}+\left(S_{1}+S_{3}\right)\left|\mathcal{A}_{\perp1}\right|^{2}+\left(S_{1}-3S_{3}\right)\left|\mathcal{A}_{\perp0}\right|^{2}+\left(S_{1}^{T}+S_{3}^{T}\right)\left|\mathcal{A}_{\perp1}^{T}\right|^{2}+\left(S_{1}^{T}-3S_{3}^{T}\right)\left|\mathcal{A}_{\perp0}^{T}\right|^{2}\notag\\
 & +\Re\left[\left(R_{1}+R_{3}\right)\mathcal{A}_{\perp1}\mathcal{A}_{\perp1}^{T*}+\left(R_{1}-3R_{3}\right)\mathcal{A}_{\perp0}\mathcal{A}_{\perp0}^{T*}\right]+\left(\perp\leftrightarrow\parallel\right),\label{eq:23}\\
\mathcal{K}_{1c} & =2\Re\left[S_{2}\mathcal{A}_{\perp1}\mathcal{A}_{\parallel1}^{*}+S_{2}^{T}\mathcal{A}_{\perp1}^{T}\mathcal{A}_{\parallel1}^{T*}\right]+\Re\left[R_{2}\mathcal{A}_{\perp1}\mathcal{A}_{\parallel1}^{T*}-\sqrt{2}R_{t}\mathcal{A}_{\perp t}\mathcal{A}_{\perp0}^{*}-\sqrt{2}R_{t}^{T}\mathcal{A}_{\perp t}\mathcal{A}_{\perp0}^{T*}+\left(\perp\leftrightarrow\parallel\right)\right],\label{eq:24}\\
\mathcal{K}_{2ss} & =2\alpha_{\Lambda_{c}}\Re\left[S_{t}\mathcal{A}_{\perp t}\mathcal{A}_{\parallel t}^{*}+\left(S_{1}-S_{3}\right)\mathcal{A}_{\perp1}\mathcal{A}_{\parallel1}^{*}+\left(S_{1}+S_{3}\right)\mathcal{A}_{\perp0}\mathcal{A}_{\parallel0}^{*}+\left(S_{1}^{T}-S_{3}^{T}\right)\mathcal{A}_{\perp1}^{T}\mathcal{A}_{\parallel1}^{T*}\right.\notag\\
 & \left.+\left(S_{1}^{T}+S_{3}^{T}\right)\mathcal{A}_{\perp0}^{T}\mathcal{A}_{\parallel0}^{T*}\right]+\alpha_{\Lambda_{c}}\Re\left[\left(R_{1}+R_{3}\right)\mathcal{A}_{\perp0}\mathcal{A}_{\parallel0}^{T*}+\left(R_{1}-R_{3}\right)\mathcal{A}_{\perp1}\mathcal{A}_{\parallel1}^{T*}+\left(\perp\leftrightarrow\parallel\right)\right],\label{eq:25}\\
\mathcal{K}_{2cc} & =2\alpha_{\Lambda_{c}}\Re\left[S_{t}\mathcal{A}_{\perp t}\mathcal{A}_{\parallel t}^{*}+\left(S_{1}+S_{3}\right)\mathcal{A}_{\perp1}\mathcal{A}_{\parallel1}^{*}+\left(S_{1}-3S\right)\mathcal{A}_{\perp0}\mathcal{A}_{\parallel0}^{*}+\left(S_{1}^{T}+S_{3}^{T}\right)\mathcal{A}_{\perp1}^{T}\mathcal{A}_{\parallel1}^{T*}\right.\notag\\
 & \left.+\left(S_{1}^{T}-3S_{3}^{T}\right)\mathcal{A}_{\perp0}^{T}\mathcal{A}_{\parallel0}^{T*}\right]+\alpha_{\Lambda_{c}}\Re\left[\left(R_{1}+R_{3}\right)\mathcal{A}_{\perp1}\mathcal{A}_{\parallel1}^{T*}+\left(R_{1}-3R_{3}\right)\mathcal{A}_{\perp0}\mathcal{A}_{\parallel0}^{T*}+\left(\perp\leftrightarrow\parallel\right)\right],\label{eq:26}\\
\mathcal{K}_{2c} & =\alpha_{\Lambda_{c}}\left[S_{2}\left|\mathcal{A}_{\perp1}\right|^{2}+S_{2}^{T}\left|\mathcal{A}_{\perp1}^{T}\right|^{2}\right]+\alpha_{\Lambda_{c}}\Re\left[R_{2}\mathcal{A}_{\perp1}\mathcal{A}_{\perp1}^{T*}-\sqrt{2}R_{t}\mathcal{A}_{\perp t}\mathcal{A}_{\parallel0}^{*}-\sqrt{2}R_{t}^{T}\mathcal{A}_{\perp t}\mathcal{A}_{\parallel0}^{T*}\right]+\left(\perp\leftrightarrow\parallel\right),\label{eq:27}\\
\mathcal{K}_{3sc} & =2\sqrt{2}\alpha_{\Lambda_{c}}\Im\left[2S_{3}\mathcal{A}_{\perp1}\mathcal{A}_{\perp0}^{*}-2S_{3}^{T}\mathcal{A}_{\perp1}^{T}\mathcal{A}_{\perp0}^{T*}+R_{3}\mathcal{A}_{\perp1}\mathcal{A}_{\perp0}^{T*}-R_{3}\mathcal{A}_{\perp0}\mathcal{A}_{\perp1}^{T*}\right]-\left(\perp\leftrightarrow\parallel\right),\label{eq:28}\\
\mathcal{K}_{3s} & =-\frac{\alpha_{\Lambda_{c}}}{\sqrt{2}}\Im\left[\sqrt{2}R_{t}\mathcal{A}_{\perp t}\mathcal{A}_{\perp1}^{*}+\sqrt{2}R_{t}^{T}\mathcal{A}_{\perp t}\mathcal{A}_{\perp1}^{T*}+2S_{2}\mathcal{A}_{\perp1}\mathcal{A}_{\parallel0}^{*}+2S_{2}^{T}\mathcal{A}_{\perp1}^{T}\mathcal{A}_{\parallel0}^{T*}\right.\notag\\
 & \left.+R_{2}\mathcal{A}_{\perp1}\mathcal{A}_{\parallel0}^{T*}-R_{2}\mathcal{A}_{\perp0}\mathcal{A}_{\parallel1}^{T*}-\left(\perp\leftrightarrow\parallel\right)\right],\label{eq:29}\\
\mathcal{K}_{4sc} & =2\sqrt{2}\alpha_{\Lambda_{c}}\Re\left[R_{3}\mathcal{A}_{\perp0}\mathcal{A}_{\parallel1}^{T*}-R_{3}\mathcal{A}_{\perp1}\mathcal{A}_{\parallel0}^{T*}-2S_{3}\mathcal{A}_{\perp1}\mathcal{A}_{\parallel0}^{*}-2S_{3}^{T}\mathcal{A}_{\perp1}^{T}\mathcal{A}_{\parallel0}^{T*}\right]-\left(\perp\leftrightarrow\parallel\right),\label{eq:30}\\
\mathcal{K}_{4s} & =\frac{\alpha_{\Lambda_{c}}}{\sqrt{2}}\Re\left[\sqrt{2}R_{t}\mathcal{A}_{\perp t}\mathcal{A}_{\parallel1}^{*}+\sqrt{2}R_{t}^{T}\mathcal{A}_{\perp t}\mathcal{A}_{\parallel1}^{T*}+2S_{2}\mathcal{A}_{\perp1}\mathcal{A}_{\perp0}^{*}+2S_{2}^{T}\mathcal{A}_{\perp1}^{T}\mathcal{A}_{\perp0}^{T*}\right.\notag\\
 & \left.+R_{2}\mathcal{A}_{\perp1}\mathcal{A}_{\perp0}^{T*}+R_{2}\mathcal{A}_{\perp0}\mathcal{A}_{\perp1}^{T*}-\left(\perp\leftrightarrow\parallel\right)\right],\label{eq:31}
\end{align}
The decay asymmetry parameter $\alpha_{\Lambda_c}$ is defined via the
angular distribution of the $\Lambda^0$ baryon in the $\Lambda_c^+$ rest frame,
\begin{equation}
\frac{1}{\Gamma_{\Lambda_c}}
\frac{d\Gamma_{\Lambda_c}}{d\cos\theta_{\Lambda}}
= \frac{1}{2}
\left(1+\alpha_{\Lambda_c}\cos\theta_{\Lambda}\right),
\end{equation}
where $\theta_{\Lambda}$ is the angle between the $\Lambda^0$ momentum
and the polarization direction of the $\Lambda_c^+$.
% \section{Phenomenology of $\Lambda_{b}\rightarrow\Lambda_{c}\tau\bar{\nu}_{\tau}$ decay}\label{sec5}
% The purpose of this section is to investigate the impact of the NP bounds computed in Section \ref{sec3} on different physical observables in $\Lambda_b\to \Lambda_{c}\tau\bar{\nu}_{\tau}$ decay. For this purpose, 
% the differential decay rate for this process reads as \cite{Datta:2017aue}
% \begin{equation}
% \frac{d\Gamma}{dq^{2}d\cos\theta_{\tau}}=\frac{G_{F}^{2}\left|V_{cb}\right|^{2}}{2048\pi^{3}}\left(1-\frac{m_{\tau}^{2}}{q^{2}}\right)\frac{\sqrt{Q_{+}Q_{-}}}{m_{1}^{3}}\sum_{\lambda_{2}}\sum_{\lambda_{\tau}}\left|M_{\lambda_{2}}^{\lambda_{\tau}}\right|^{2},\label{DecayRate}
% \end{equation}
% where 
% \begin{align*}
% q & =p_{1}-p_{2},\quad Q_{\pm}=\left(m_{1}\pm m_{2}\right)^{2}-q^{2}
% \end{align*}
% and the helicity amplitude $M_{\lambda_{2}}^{\lambda_{\tau}}$ is
% written as
% \begin{equation}
% M_{\lambda_{2}}^{\lambda_{\tau}}=H_{\lambda_{2}}^{SP}L^{\lambda_{\tau}}+\sum_{\lambda}\eta_{\lambda}H_{\lambda_{2},\lambda}^{VA}L_{\lambda}^{\lambda_{\tau}}+\sum_{\lambda,\lambda'}\eta_{\lambda}H_{\lambda_{2},\lambda,\lambda'}^{\left(T\right)\lambda_{1}}L_{\lambda,\lambda'}^{\lambda_{\tau}}.
% \end{equation}
% Here, $\left(\lambda,\lambda'\right)$ indicate the helicities of the
% virtual vector boson, and $\lambda_{2}$ and $\lambda_{\tau}$ are
% the helicities of the $\Lambda_{c}-$baryon and $\tau-$lepton, respectively. The scalar/pseudo-scalar-type, vector/axial-vector-type, and tensor-type hadronic helicity amplitudes are defined as:
% \begin{equation}
% H_{\lambda_{2}}^{SP}  =H_{\lambda_{2}}^{S}+H_{\lambda_{2}}^{P},\hspace{1.1cm}
% H_{\lambda_{2}}^{S}  =\left(\widetilde{C}_{S_{L}}+\widetilde{C}_{S_{R}}\right)\left\langle \Lambda_{c}\left|\bar{c}b\right|\Lambda_{b}\right\rangle ,\hspace{1.1cm}
% H_{\lambda_{2}}^{P}  =\left(-\widetilde{C}_{S_{L}}+\widetilde{C}_{S_{R}}\right)\left\langle \Lambda_{c}\left|\bar{c}b\right|\Lambda_{b}\right\rangle ,\label{eq:hscalar}
% \end{equation}
% \begin{eqnarray}
% H_{\lambda_{2},\lambda}^{VA}  &=&H_{\lambda_{2},\lambda}^{V}-H_{\lambda_{2},\lambda}^{A},\notag \\ 
% H_{\lambda_{2},\lambda}^{V} &=&\left(1+\widetilde{C}_{V_{L}}+\widetilde{C}_{V_{R}}\right)\epsilon^{*\mu}\left(\lambda\right)\left\langle \Lambda_{c}\left|\bar{c}\gamma_{\mu}b\right|\Lambda_{b}\right\rangle ,\hspace{1.2cm}
% H_{\lambda_{2},\lambda}^{A} =\left(1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}\right)\epsilon^{*\mu}\left(\lambda\right)\left\langle \Lambda_{c}\left|\bar{c}\gamma_{\mu}\gamma_{5}b\right|\Lambda_{b}\right\rangle ,\label{eq:hvector}
% \end{eqnarray}
% and
% \begin{eqnarray}
% H_{\lambda_{2},\lambda,\lambda'}^{\left(T\right)\lambda_{1}} &=&H_{\lambda_{2},\lambda,\lambda'}^{\left(T1\right)\lambda_{1}}-H_{\lambda_{2},\lambda,\lambda'}^{\left(T2\right)\lambda_{1}},
% \notag \\
% H_{\lambda_{2},\lambda,\lambda'}^{\left(T1\right)\lambda_{1}} &=&\widetilde{C}_{T}\epsilon^{*\mu}\left(\lambda\right)\epsilon^{*\mu}\left(\lambda'\right)\left\langle \Lambda_{c}\left|\bar{c}i\sigma_{\mu\nu}b\right|\Lambda_{b}\right\rangle ,\hspace{2.2cm}
% H_{\lambda_{2},\lambda,\lambda'}^{\left(T2\right)\lambda_{1}} =\widetilde{C}_{T}\epsilon^{*\mu}\left(\lambda\right)\epsilon^{*\mu}\left(\lambda'\right)\left\langle \Lambda_{c}\left|\bar{c}i\sigma_{\mu\nu}\gamma_{5}b\right|\Lambda_{b}\right\rangle .\label{eq:htensor}
% \end{eqnarray}

% The leptonic parts of the amplitude can be written as:
% \begin{align}
% L^{\lambda_{\tau}} & =\left\langle \tau\bar{\nu}_{\tau}\left|\bar{\tau}\left(1-\gamma_{5}\right)\nu_{\tau}\right|0\right\rangle ,\nonumber \\
% L_{\lambda}^{\lambda_{\tau}} & =\epsilon^{*\mu}\left(\lambda\right)\left\langle \tau\bar{\nu}_{\tau}\left|\bar{\tau}\gamma_{\mu}\left(1-\gamma_{5}\right)\nu_{\tau}\right|0\right\rangle ,\nonumber \\
% L_{\lambda,\lambda'}^{\lambda_{\tau}} & =-\epsilon^{*\mu}\left(\lambda\right)\epsilon^{*\mu}\left(\lambda'\right)\left\langle \tau\bar{\nu}_{\tau}\left|\bar{\tau}i\sigma_{\mu\nu}\left(1-\gamma_{5}\right)\nu_{\tau}\right|0\right\rangle ,
% \end{align}
% where $\epsilon^{\mu}$ defines the polarization vector of the virtual vector boson, and its different components are given in Appendix \ref{hspa}.

% In this work, we make use of the helicity-based definition of the $\Lambda_{b}\rightarrow\Lambda_{c}$ form factors as introduced in \cite{Feldmann:2011xf} and then extended them to include tensor form factors from \cite{Detmold:2016pkz}. The matrix elements of the vector and axial
% vector currents are expressed using six helicity form factors: $F_{+}$, $F_{\perp}$, $F_{0}$, $G_{+}$, $G_{\perp}$, and $G_{0}$; and four tensor form factor $h_{+}$, $\widetilde{h}_{+}$, $h_{\perp}$, and $\widetilde{h}_{\perp}$ . There explicit interpolation with $q^2$ is summarized in Appendix \ref{hspa}.  Using the spinors for $\Lambda_b$ and $\Lambda_c$ along with the kinematical relations given in \ref{hspa}, the scalar and pseudo-scalar hadronic helicity amplitudes are
% \begin{equation}
% H_{\pm1/2}^{SP}=F_{0}\left(\widetilde{C}_{S_{L}}+\widetilde{C}_{S_{R}}\right)\frac{\sqrt{Q_{+}}}{m_{b}-m_{c}}m_{-}\pm G_{0}\left(\widetilde{C}_{S_{L}}-\widetilde{C}_{S_{R}}\right)\frac{\sqrt{Q_{-}}}{m_{b}+m_{c}}m_{+}.
% \end{equation}
% Similarly, the vector and axial-vector hadronic helicity amplitudes will become
% \begin{align}
% H_{\pm1/2,t}^{VA} & =\frac{1}{\sqrt{q^{2}}}\left(F_{0}\left(1+\widetilde{C}_{V_{L}}+\widetilde{C}_{V_{R}}\right)\sqrt{Q_{+}}m_{-}\mp G_{0}\left(1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}\right)\sqrt{Q_{-}}m_{+}\right),\nonumber \\
% H_{\pm1/2,0}^{VA} & =\frac{1}{\sqrt{q^{2}}}\left(F_{+}\left(1+\widetilde{C}_{V_{L}}+\widetilde{C}_{V_{R}}\right)\sqrt{Q_{-}}m_{+}\mp G_{+}\left(1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}\right)\sqrt{Q_{+}}m_{-}\right),\nonumber \\
% H_{\pm1/2,\pm}^{VA} & =\sqrt{2}\left(F_{\perp}\left(1+\widetilde{C}_{V_{L}}+\widetilde{C}_{V_{R}}\right)\sqrt{Q_{-}}\mp G_{\perp}\left(1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}\right)\sqrt{Q_{+}}\right).
% \end{align}
% Likewise, the non-zero tensor hadronic helicity amplitudes are
% \begin{align*}
% H_{\pm1/2,t,0}^{\left(T\right)\pm1/2} & =-H_{\pm1/2,+,-}^{\left(T\right)\pm1/2}=\widetilde{C}_{T}\left(h_{+}\sqrt{Q_{-}}\pm\widetilde{h}_{+}\sqrt{Q_{+}}\right),\\
% H_{\pm1/2,t,\pm}^{\left(T\right)\mp1/2} & =\mp H_{\pm1/2,0,\pm}^{\left(T\right)\mp1/2}=\widetilde{C}_{T}\frac{\sqrt{2}}{\sqrt{q^{2}}}\left(h_{\perp}\sqrt{Q_{-}}m_{+}\pm\widetilde{h}_{\perp}\sqrt{Q_{+}}m_{-}\right),
% \end{align*}
% and
% \begin{equation}
% H_{\lambda_{2},\lambda,\lambda'}^{\left(T\right)\lambda_{1}}=-H_{\lambda_{2},\lambda',\lambda}^{\left(T\right)\lambda_{1}}.
% \end{equation}

% In the di-leptonic rest frame, the momenta of the final state leptons, and the corresponding spinors are defined in Appendix \ref{hspa-2}. Using them, the non-zero leptonic helicity amplitudes are computed as follows:
% \begin{align}
% L^{1/2} & =2\sqrt{q^{2}}v,\quad
% L_{t}^{1/2}  = 2m_{\tau}v,\quad
% L_{0}^{1/2} =-2m_{\tau}v\cos\theta_{\tau},\quad
% L_{0}^{-1/2} =2\sqrt{q^{2}}v\sin\theta_{\tau},\nonumber \\
% L_{\pm}^{1/2} & =\mp\sqrt{2}m_{\tau}v\sin\theta_{\tau},\quad
% L_{\pm}^{-1/2} =\sqrt{2q^{2}}v\left(-1\mp \cos\theta_{\tau}\right),\quad
% L_{t,0}^{1/2} =L_{+,-}^{1/2}=-2\sqrt{q^{2}}v\cos\theta_{\tau},\nonumber \\
% L_{t,0}^{-1/2} & =L_{+,-}^{-1/2}=2m_{\tau}v\sin\theta_{\tau},\quad
% L_{t,\pm}^{1/2} =\mp L_{0,\pm}^{1/2}=\mp\sqrt{2q^{2}}v\sin\theta_{\tau},\quad
% L_{t,\pm}^{-1/2}=\mp L_{0,\pm}^{1/2}=\sqrt{2}m_{\tau}v\left(-1\mp \cos\theta_{\tau}\right)
% \end{align}
% where 
% \begin{equation}
% L_{\lambda,\lambda'}^{\lambda_{2}}=-L_{\lambda',\lambda}^{\lambda_{2}}.
% \end{equation}


\section{Numerical Analysis }\label{Num-anlaysis}
In this section, we analyze the above-mentioned angular observables within the SM and in the presence of NP, incorporating the constraints on the allowed parameter space of various NP scenarios derived from the latest HFLAV results discussed in Sec.~\ref{subsec3}, together with the collider bounds presented in Sec.~\ref{subcolb}.

Figure~\ref{phen-2d} illustrates the $q^{2}$ dependence of the angular observables $\mathcal{K}_{i}$, with 
$i = 1ss,\,1cc,\,1c,\,2ss,\,2cc,\,2c,\,3sc,\,3s,\,4sc,\,4s$, 
evaluated in the SM and for different two-dimensional NP benchmark scenarios listed in Table~\ref{2d-table-1}. 
In the presence of NP, deviations from the SM predictions are shown as colored bands, each corresponding to a specific combination of Wilson coefficients:
$(C_{V_L}, C_{S_R})$, 
$(C_{V_L}, C_{S_L}=-4C_T)$, 
$\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$, 
and $(C_{S_L}, C_{S_R})$.
With reference to the SM predictions, the impact of NP on these observables can be summarized as follows:
%
\begin{itemize}
\item \textbf{$\bm{\mathcal{K}_{1ss}}$:}  
NP effects are most pronounced in the intermediate $q^{2}$ region for all scenarios. 
The $\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ scenario yields the largest upward shift, while the remaining scenarios induce comparatively mild deviations. 
Consequently, precise measurements of $\mathcal{K}_{1ss}$ can effectively constrain NP scenarios and, in particular, discriminate $\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ interactions from other possibilities.

\item \textbf{$\bm{\mathcal{K}_{1cc}}$:}  
A noticeable deviation is observed only in the 
$\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ scenario, which induces a downward shift of approximately $0.005$ with an uncertainty of $0.002$ (corresponding to about $2.5\sigma$). 
The $(C_{V_L},C_{S_R})$ scenario leads to a minor upward shift. 
Overall, $\mathcal{K}_{1cc}$ remains relatively stable and does not serve as a strong discriminator among $(C_{S_L}, C_{S_R})$ NP fits, although it shows moderate sensitivity to $\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ contributions.

\item \textbf{$\bm{\mathcal{K}_{1c}}$:}  
This observable exhibits the strongest sensitivity to NP effects. 
The $\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ scenario produces a significant downward shift of about $-0.05$, while the $(C_{S_L},C_{S_R})$ scenario leads to a clear upward shift of approximately $+0.032$. 
In contrast, the $(C_{V_L},C_{S_R})$ and $(C_{V_L},C_{S_L}=-4C_T)$ scenarios remain consistent with the SM within uncertainties. 
Thus, $\mathcal{K}_{1c}$ serves as a powerful discriminator between different NP scenarios, particularly between $\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ and $(C_{S_L}, C_{S_R})$ interactions.

\item \textbf{$\bm{\mathcal{K}_{2ss}}$:}  
This observable is largely insensitive to $(C_{V_L}, C_{S_R})$ NP scenarios but exhibits strong sensitivity to the 
$\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ contributions, which produce a large and highly significant upward shift across the entire $q^{2}$ region. 
The $(C_{S_L},C_{S_R})$ scenario induces only a mild reduction.

\item \textbf{$\bm{\mathcal{K}_{2cc}}$:}  
The observable remains close to the SM prediction for most NP scenarios. 
The largest deviation, corresponding to approximately $1.7\sigma$, occurs for the 
$\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ case, where the distribution is shifted to values around $0.25$--$0.30$ over the full $q^{2}$ range.

\item \textbf{$\bm{\mathcal{K}_{2c}}$:}  
A moderate sensitivity to NP effects is observed. 
The $\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ scenario produces the largest upward shift (about $1.8\sigma$), reducing the magnitude of the negative values across all $q^{2}$. 
The maximum separation from the SM occurs in the intermediate region, $q^{2}\approx6$--$11~\mathrm{GeV}^{2}$. 
Other scenarios yield smaller negative shifts. 
Hence, $\mathcal{K}_{2c}$ provides a useful probe of $\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ interference effects.

\item \textbf{$\bm{\mathcal{K}_{3sc}}$:}  
This observable remains consistent with zero within uncertainties for all scenarios. 
The largest apparent effect, of order $0.03$, appears in the 
$\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ scenario.

\item \textbf{$\bm{\mathcal{K}_{3s}}$:}  
The observable shows negligible sensitivity to NP and exhibits no significant shape distortion, making it less effective for NP discrimination.

\item \textbf{$\bm{\mathcal{K}_{4sc}}$:}  
A pronounced negative dip is observed around $q^{2}\approx6$--$10~\mathrm{GeV}^{2}$, reaching values close to $-0.04$ in the 
$\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ scenario. 
The $(C_{V_L},C_{S_L}=-4C_T)$ and $(C_{S_L},C_{S_R})$ scenarios show moderate upward shifts, although the observable remains negative throughout the entire $q^{2}$ range. 
Thus, $\mathcal{K}_{4sc}$ provides a sensitive probe of $\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ effects.

\item \textbf{$\bm{\mathcal{K}_{4s}}$:}  
This observable exhibits a smooth negative distribution over the full $q^{2}$ region,  reaching values near $-0.14$. 
While some NP scenarios induce mild shifts, the overall shape remains largely unchanged. 
Notably, the 
$\left(\Re[C_{S_L}=4C_T],\,\Im[C_{S_L}=4C_T]\right)$ scenario in the intermediate $q^{2}$ region and the $(C_{V_L},C_{S_L}=-4C_T)$ scenario at low $q^{2}$ show significant deviations from the SM.
\end{itemize}

The averaged values of the angular observables $\mathcal{K}_{i}$,
with $i=1ss,\,1cc,\,1c,\,2ss,\,2cc,\,2c,\,3sc,\,3s,\,4sc,\,4s$,
evaluated at the BFPs for the two-dimensional NP scenarios,
are listed in Table~\ref{2d-obs-table}.
We observe that, except for the total decay rate, the uncertainties arising from the input parameters do not mimic the effects induced by NP.
Consequently, these angular observables provide clean and robust probes for establishing NP in these FCCC decays.


\begin{table}[H]
\centering{}%
\renewcommand{\arraystretch}{1.5}
\begin{tabular}{|c|c|c|c|c|c|}
\hline 
WCs & SM & $\left(C_{V_{L}},C_{S_{R}}\right)$ & $\left(C_{V_{L}},C_{S_{L}}=-4C_{T}\right)$ & $\left(\Re\left[C_{S_{L}}=4C_{T}\right],\Im\left[C_{S_{L}}=4C_{T}\right]\right)$ & $\left(C_{S_{L}},C_{S_{R}}\right)$ \tabularnewline
\hline 
\hline 
BFP & $C_{i}=0$ & $\left(0.06,0.01\right)$ & $\left(0.06,0.01\right)$ & $\left(-0.04,-0.29\right)$ & $\left(-0.19,0.24\right)$
\tabularnewline
\hline 
$\mathcal{K}_{1ss} $ & $0.323\pm0$ & $0.323\pm0.001$ & $0.323\pm0.001$ & $0.325\pm0.001$ & $0.324\pm0.001$
\tabularnewline
\hline 
$\mathcal{K}_{1cc} $ & $0.354\pm0$ & $0.353\pm0.002$ & $0.353\pm0.002$ & $0.349\pm0.002$ & $0.351\pm0.001$
\tabularnewline\hline 
$\mathcal{K}_{1c} $ & $0.224\pm0.004$ & $0.226\pm0.025$ & $0.222\pm0.008$ & $0.191\pm0.025$ & $0.256\pm0.043$
\tabularnewline\hline 
$\mathcal{K}_{2ss} $ & $-0.240\pm0.003$ & $-0.240\pm0.003$ & $-0.236\pm0.017$ & $-0.171\pm0.041$ & $-0.256\pm0.033$
\tabularnewline\hline 
$\mathcal{K}_{2cc} $ & $-0.279\pm0.003$ & $-0.278\pm0.009$ & $-0.275\pm0.0017$ & $-0.211\pm0.039$ & $-0.290\pm0.031$
\tabularnewline\hline 
$\mathcal{K}_{2c} $ & $-0.274\pm0.002$ & $-0.278\pm0.033$ & $-0.276\pm0.0014$ & $-0.215\pm0.033$ & $-0.294\pm0.013$
\tabularnewline\hline 
$\mathcal{K}_{3sc} $ & $0\pm0$ & $0\pm0$ & $0\pm0$ & $\pm0.017\pm0.034$ & $0\pm0.009$
\tabularnewline\hline 
$\mathcal{K}_{3s} $ & $0\pm0$ & $0\pm0$ & $0\pm0$ & $0\pm0.001$ & $0\pm0$
\tabularnewline\hline 
$\mathcal{K}_{4sc} $ & $-0.024\pm0$ & $-0.023\pm0.003$ & $-0.024\pm0.005$ & $-0.026\pm0.007$ & $-0.021\pm0.002$
\tabularnewline\hline 
$\mathcal{K}_{4s} $ & $-0.149\pm0.003$ & $-0.152\pm0.025$ & $-0.156\pm0.023$ & $-0.111\pm0.021$ & $-0.136\pm0.016$
\tabularnewline
\hline 
\end{tabular}\caption{\label{2d-obs-table} BFPs for the two-dimensional NP scenarios obtained under the constraint
$\mathcal{B}\!\left(B_{c}^{-}\to\tau^{-}\bar{\nu}_{\tau}\right)<60\%$, together with the corresponding
predictions for the full set of angular observables $\mathcal{K}_{i}$ with
$i=1ss,\,1cc,\,1c,\,2ss,\,2cc,\,2c,\,3sc,\,3s,\,4sc,\,4s$.
The quoted uncertainties include contributions from hadronic form factors,
other input parameters, and the uncertainties in the BFP determination.
}
\end{table}


\begin{figure}[H]
\centering 
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{o1si.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{o2s.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{o3s.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{o4s.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{o5s.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{o6s.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{o7s.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{o8s.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{o9s.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{o10s.pdf}
\caption{}
\end{subfigure}

\caption{\label{phen-2d}The angular observables $\mathcal{K}_{i}(q^{2})$ are shown as functions of $q^{2}$ both within the SM and for various NP scenarios.
The bands of the curves reflect the theoretical uncertainties arising from the hadronic form factors and other input parameters.
The SM predictions are represented by the black bands, while the NP scenarios are indicated by colored bands.
}
\end{figure}




\section{Correlating different Physical observables}\label{correlation}
% In Section \ref{sec1}, we have mentioned that the measurements of $R_{\tau/\ell}\left(\Lambda_{c}\right)$, and $R_{\tau/\mu}\left(J/\psi\right)$ are prone to various uncertainties, therefore, it is useful to express them in terms of the \textcolor{red}{observables
% with better theoretical control}, \textit{i.e.,} $R_{\tau/\mu,e}\left(D\right)$ and $R_{\tau/\mu,e}\left(D^*\right)$. For the first time, these relations are derived in \cite{Fedele:2022iib} and named as the sum rules. In our case, we can write the similar sum rule from the Eqs. (\ref{eqn1}, \ref{eqn2} and \ref{eqn7}) as:
% \begin{equation}
% \frac{R_{\tau/\ell}\left(\Lambda_{c}\right)}{R_{\tau/\ell}^{\text{SM}}\left(\Lambda_{c}\right)}=0.275\frac{R_{\tau/{\mu,e}}\left(D\right)}{R^{\text{SM}}_{\tau/{\mu,e}}\left(D\right)}+0.725\frac{R_{\tau/{\mu,e}}\left(D^{*}\right)}{R^{\text{SM}}_{\tau/{\mu,e}}\left(D^{*}\right)}+x_{1},\label{sum-n1}
% \end{equation}
% where small remainder $x_{1}$ can be approximated in terms of WCs at a scale
% $m_{b}$ as \cite{Blanke:2018yud}:
% \begin{eqnarray}
% x_{1}& = &\left.\Re\left[\left(1+C_{V_{L}}\right)\left(0.607C_{V_{R}}^{*}+0.011C_{S_{R}}^{*}+0.341C_{T}^{*}\right)\right]+\Re\left[C_{V_{R}}\left(0.090C_{S_{L}}^{*}+0.080C_{S_{R}}^{*}+0.202C_{T}^{*}\right)\right]\right.\nonumber \\
%  &  & \left.+0.013\left(\left|C_{S_{R}}\right|^{2}+\left|C_{S_{L}}\right|^{2}\right)+0.520\Re\left[C_{S_{L}}\left(C_{S_{R}}\right)^{*}\right]-0.044\left|C_{T}\right|^{2}\right.\label{rem1}.
% \end{eqnarray}
% In Eq. (\ref{sum-n1}), we can see that in $R_{\tau/\ell}\left(\Lambda_c\right)$, the relative weight of the $R_{\tau/{\mu,e}}\left(D^*\right)/R^{\text{SM}}_{\tau/{\mu,e}}\left(D^*\right)$ is $72\%$, and hence with better control over the errors in its measurements and the SM predictions, will help us to predict $R_{\tau/\ell}\left(\Lambda_c\right)$ to good accuracy. Depending on the observation that  $R_{\tau/\mu}\left(J/\psi\right)$ exhibits the same behaviour as $R_{\tau/\ell}\left(\Lambda_c\right)$, therefore, it will be interesting to see if we can establish a similar relation for $R_{\tau/\mu}\left(J/\psi\right)$. The required some rule can be obtained from equations \ref{eqn1}, \ref{eqn2}, and \ref{eqn5} which can be written as follows:
% \begin{align}
% \frac{R_{\tau/\mu}\left(J/\psi\right)}{R^{\text{SM}}_{\tau/\mu}\left(J/\psi\right)} & =0.006\frac{R_{\tau/{\mu,e}}\left(D\right)}{R^{\text{SM}}_{\tau/{\mu,e}}\left(D\right)}+0.994\frac{R_{\tau/\mu}\left(D^{*}\right)}{R^{\text{SM}}_{\tau/{\mu,e}}\left(D^{*}\right)}+x_{2},\label{sum2}
% \end{align}
% where the remainder $x_{2}$ can be written as
% \begin{eqnarray}
% x_{2}& = &\left.-\Re\left[\left(1+C_{V_{L}}\right)\left(0.001C_{V_{R}}^{*}+0.018C_{S_{R}}^{*}+0.259C_{T}^{*}\right)\right]+\Re\left[C_{V_{R}}\left(0.091C_{S_{L}}^{*}-0.109C_{S_{R}}^{*}+0.005C_{T}^{*}\right)\right]\right.\nonumber \\
%  &  & \left.-0.006\left(\left|C_{S_{R}}\right|^{2}+\left|C_{S_{L}}\right|^{2}\right)-13.701\left|C_{T}\right|^{2}\right.\label{rem2}.
% \end{eqnarray}
% In Eq. (\ref{sum2}), the LFU ratio $R_{\tau/\mu}\left(J/\psi\right)$ normalized with the corresponding SM prediction, has negligible dependence on the $R_{\tau/{\mu,e}}\left(D\right)/R^{\text{SM}}_{\tau/{\mu,e}}\left(D\right)$, therefore, the refined measurement of the $R_{\tau/{\mu,e}}\left(D^*\right)$ will help us to get good control over $R_{\tau/\mu}\left(J/\psi\right)$. Also, we can see that if $R_{\tau/{\mu,e}}\left(D\right)$ and $R_{\tau/{\mu,e}}\left(D^{*}\right)$ are enhanced
% over their SM values, it follows that $R_{\tau/\mu}\left(J/\psi\right)$ must also experience an enhancement. By incorporating the BFPs of Tables \ref{1d-table} and \ref{2d-table-1}, we find that remainders $x_1$ and $x_2$ in Eqs. (\ref{rem1} and \ref{rem2}), respectively, both are approximated $<10^{-3}$ for all the
% NP WCs, which ensure the validity of these sum rules. Being model-independent, these sum rules remain valid in any NP model, indicating that future measurements of $R_{\tau/\ell}\left(\Lambda_{c}\right)$, and $R_{\tau/\ell}\left(J/\psi\right)$ can serve as essential crosschecks for the measurements of $R_{\tau/{\mu,e}}\left(D\right)$ and $R_{\tau/{\mu,e}}\left(D^{*}\right)$. Using the values from Eqs. (\ref{HFLAV-RDDs},\ref{SM-RDDs}) in Eq. (\ref{sum-n1}), we can predict
% \begin{align*}
% R_{\tau/\ell}\left(\Lambda_{c}\right) & =R^{\text{SM}}_{\tau/\ell}\left(\Lambda_{c}\right)\left(1.135\pm0.045\right) =0.368\pm0.015\pm0.005,
% \end{align*}
% as given in ref. \cite{Fedele:2022iib}. In this result, the first error comes from the experimental measurements in LFU ratios of $D$ and $D^*$ and the second is due to the form factors uncertainties in the SM predictions of these corresponding ratios. The numerical value is not much different from the previously reported which indicate that the most recent data of $R_{\tau/{\mu,e}}\left(D^{*}\right)$ supports the validity of the above sum rule. Similarly, for the other sum rule (c.f. Eqs. (\ref{sum2})), we have
% \begin{align*}
% R_{\tau/\mu}\left(J/\psi\right) & =R^{\text{SM}}_{\tau/\mu}\left(J/\psi\right) \left(1.130\pm0.052\right) =0.292\pm0.013\pm0.043.
% \end{align*}
% It is evident that the SM value of $R_{\tau/\mu}\left(J/\psi\right)$ as well as its updated value derived from the sum rule using the latest data, both fall below the experimental measurements and exhibit a consistent pattern, similar to that of observed in $R_{\tau/{\mu,e}}\left(D^{*}\right)$.  However, in the case of $R_{\tau/\mu}\left(J/\psi\right)$, even though its tensor form factors are not precisely calculated yet, the theoretically predicted values are quite small compared to its experimental value with large uncertainties, $0.71 \pm 0.18\pm0.17$. We expect several planned and current experiments to explore this value further.

% \textcolor{red}{We compared our results with some recent literature and the corresponding results are appended in  Table \ref{tab-comp}. This presents a direct comparison between our updated 1D fit results (with real WCs at scale $2\text{TeV}$) and those reported in ref. \cite{Endo:2025cvu} at scale $\mu_{b}$. For each scenario ($C_{S_R}$, $C_{S_L}$, and $C_{T}$), we list the best-fit points (BFPs), pull values, and the deviations in remainders of the sum rules $x_1$ and $x_2$. Since our analysis focuses on real WCs, we note that only the $C_{S_{R}}$ scenario directly match our framework. In our analysis, the $C_{S_{R}}$ scenario yields the BFP of $0.40$ and a pull of $3.17\sigma$, indicating a moderate improvement over the SM. This is consistent with \cite{Endo:2025cvu}, where a pull of $3.9$ was reported. For $C_{S_L}$, we obtain $C_{S_L}=0.38$ ($pull=2.6$), while \cite{Endo:2025cvu} uses a complex WC $-0.57\pm0.86i$ ($pull=4.3$). The comparison is limited due to the real–complex difference, but both fits yield $10^{-3}$ sum rule remainders. In the $C_T$ scenario, our result $C_T=-0.17$ ($pull=3.3$) differs from the reference value $0.02\pm0.13i$ ($pull=3.8$). However, we note that the remainders $x_1$ and $x_2$ between both fits are $1-2\%$ and $0.1\%$ respectively.}

% \begin{table}[h]
% \centering{}
% \begin{tabular}{|c|c|c|c|c|}
% \hline 
% WCs & BFP & Pull & $x_{1}$ & $x_{2}$\tabularnewline
% \hline 
% \hline 
% \multirow{2}{*}{$C_{S_{R}}$} & $0.40\left(2TeV\right)$ & $3.2$ & $0.002$ & $-0.003$\tabularnewline
% \cline{2-5} \cline{3-5} \cline{4-5} \cline{5-5} 
%  & $0.182\left(\mu_{b}\right)$ & $3.9$ & $0.0007$ & $-0.001$\tabularnewline
% \hline 
% \multirow{2}{*}{$C_{S_{L}}$} & $0.38\left(2TeV\right)$ & $2.6$ & $0.000$ & $0.000$\tabularnewline
% \cline{2-5} \cline{3-5} \cline{4-5} \cline{5-5} 
%  & $-0.57\pm0.86i\left(\mu_{b}\right)$ & $4.3$ & $0.001$ & $-0.0008$\tabularnewline
% \hline 
% \multirow{2}{*}{$C_{T}$} & $-0.17\left(2TeV\right)$ & $3.3$ & $-0.010$ & $0.019$\tabularnewline
% \cline{2-5} \cline{3-5} \cline{4-5} \cline{5-5} 
%  & $0.02\pm0.13i\left(\mu_{b}\right)$ & $3.8$ & $0.001$ & $0.008$\tabularnewline
% \hline 
% \end{tabular}\caption{\label{tab-comp}\textcolor{red}{The results of 1-dimensional fit for real WCs scenarios which include
% BFPs, pull and remainder of sum rule for $R_{\tau/\ell}\left(\Lambda_{c}\right)$ $x_{1}$ and $R_{\tau/\mu}\left(J/\psi\right)$ $x_{2}$ for
% set $\mathcal{S}_1$ at scale $2TeV$ are shown in each first sub-row of each scenario.
% Second sub-row for each scenario is results taken from \cite{Endo:2025cvu}
% at scale $\mu_{b}$.}}

% \end{table}

% \textcolor{red}{Furthermore, a comparison with \cite{Iguro:2024hyk} is included in Table XIV. Our fitted values for $C_{V_L}=0.31$ ($pull=3.9$), $C_{S_R}=0.40$ ($pull=3.2$), and $C_{T}=-0.17$ ($pull=3.3$) show good agreement with the corresponding values $0.42$, $0.77$, and $0.30$ from \cite{Iguro:2024hyk}, with all scenarios yielding small $x_{1}$ and $x_{2}$ sum rule remainders. This supports the consistency of our results with existing literature at the scale $2\text{TeV}$.}

% \begin{table}[h]
% \centering{}
% \begin{tabular}{|c|c|c|c|c|}
% \hline 
% WCs & BFP & Pull & $x_{1}$ & $x_{2}$\tabularnewline
% \hline 
% \hline 
% $C_{V_{L}}$ & $0.31\left(0.15\right)$ & $3.9$ & $0.000$ & $0.000$\tabularnewline
% \hline 
%  & $0.42\left(0.12\right)$ & - & $0.000$ & $0.000$\tabularnewline
% \hline 
% $C_{V_{R}}$ & $-0.26\left(-0.26\right)$ & $1.85$ & $-0.032$ & $0.0001$\tabularnewline
% \hline 
%  & $0.51\left(0.15\right)$ & - & $0.062$ & $-0.0001$\tabularnewline
% \hline 
% $C_{S_{L}}$ & $0.38\left(0.27\right)$ & $2.6$ & $0.000$ & $0.000$\tabularnewline
% \hline 
%  & $0.80\left(0.22\right)$ & - & $0.001$ & $-0.001$\tabularnewline
% \hline 
% $C_{S_{R}}$ & $0.40\left(0.23\right)$ & $3.2$ & $0.002$ & $-0.003$\tabularnewline
% \hline 
%  & $0.77\left(0.22\right)$ & - & $0.004$ & $-0.006$\tabularnewline
% \hline 
% $C_{T}$ & $-0.17\left(0.09\right)$ & $3.3$ & $-0.010$ & $0.019$\tabularnewline
% \hline 
%  & $0.30\left(0.07\right)$ & - & $0.017$ & $0.021$\tabularnewline
% \hline 
% \end{tabular}

% \caption{\textcolor{red}{The results of 1-dimensional fit for real WCs scenarios which include
% BFPs, pull and remainders of sum rule $x_{1}$ and $x_{2}$ for $R_{\tau/\ell}\left(\Lambda_{c}\right)$  and $R_{\tau/\mu}\left(J/\psi\right)$, respectively, for
% set $\mathcal{S}_1$ at scale $2\text{TeV}$in the first sub-row of each scenario.
% The second sub-row in each scenario shows the corresponding results from \cite{Iguro:2024hyk}, which are
% also calculated at $2\text{TeV}$.}}

% \end{table}

In this section, we investigate the correlations among the angular observables
$\mathcal{K}_{i}$ with
$i=1ss,\,1cc,\,1c,\,2ss,\,2cc,\,2c,\,3sc,\,3s,\,4sc,\,4s$
using the $1\sigma$ allowed parameter space of the two-dimensional NP scenarios.
Such correlation studies provide complementary and incisive information beyond
individual observable analyses.
The explicit expressions employed in this analysis are given in
Appendix~\ref{obsRLc}, and the resulting correlation plots are shown in
Fig. \ref{corr-2d} - \ref{corr-2d-2}.

We find that the correlations exhibit clear NP-dependent patterns.
For the scenario
$\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ (cyan),
an inverse correlation is observed for
$\mathcal{K}_{1ss}$--$\mathcal{K}_{1cc}$ and
$\mathcal{K}_{1cc}$--$\mathcal{K}_{4s}$,
whereas direct correlations appear in
$\mathcal{K}_{1ss}$--$\mathcal{K}_{4s}$,
$\mathcal{K}_{2ss}$--$\mathcal{K}_{2c}$,
$\mathcal{K}_{2cc}$--$\mathcal{K}_{2c}$, and
$\mathcal{K}_{2ss}$--$\mathcal{K}_{4s}$.
In contrast, for the scenario
$\left(C_{S_{L}},C_{S_{R}}\right)$ (orange),
$\mathcal{K}_{1ss}$--$\mathcal{K}_{1cc}$ and
$\mathcal{K}_{1c}$--$\mathcal{K}_{2ss}$ show inverse correlations,
while $\mathcal{K}_{1ss}$--$\mathcal{K}_{4sc}$ and
$\mathcal{K}_{2cc}$--$\mathcal{K}_{4s}$ exhibit direct correlations,
highlighting their distinct dynamical origins.

We now examine the correlations among the observables $\mathcal{K}_{1c}$, $\mathcal{K}_{2ss}$,
$\mathcal{K}_{2cc}$, and $\mathcal{K}_{4s}$, which display the strongest NP sensitivity,
as already indicated in Sec.~\ref{Num-anlaysis}.
The pair $\mathcal{K}_{1c}$--$\mathcal{K}_{2ss}$ shows an inverse correlation for
$\left(C_{S_{L}},C_{S_{R}}\right)$ and a pronounced negative correlation for
$\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$.
A similar behavior is observed for $\mathcal{K}_{1c}$--$\mathcal{K}_{2cc}$,
with a negative correlation in the $\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ case.
Conversely, $\mathcal{K}_{1c}$--$\mathcal{K}_{4s}$ exhibits a strong negative
correlation for the $\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ scenario, but a strong positive
correlation for the $\left(C_{S_{L}},C_{S_{R}}\right)$ case, signaling distinct interference
patterns.

For $\mathcal{K}_{2ss}$--$\mathcal{K}_{2cc}$, both NP scenarios $\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ and $\left(C_{S_{L}},C_{S_{R}}\right)$ lead to a direct
correlation, while $\mathcal{K}_{2ss}$--$\mathcal{K}_{4s}$ displays a strong
positive correlation in the $\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ and a pronounced negative
correlation in the $\left(C_{S_{L}},C_{S_{R}}\right)$ scenario.
Similarly, $\mathcal{K}_{2cc}$--$\mathcal{K}_{4s}$ remains directly correlated
for the $\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ case but becomes inversely correlated for $\left(C_{S_{L}},C_{S_{R}}\right)$.
These correlation flips shows contrasting behaviors underscore the sensitivity of angular correlations
to the phase structure of NP couplings.

The inverse-correlation patterns observed in the $\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ scenario point to destructive helicity interference and provide
indirect sensitivity to possible CP-violating phases in the NP sector.
In contrast, the $\left(C_{S_{L}},C_{S_{R}}\right)$ scenario predominantly yields constructive
correlations, consistent with CP-conserving interactions.
Therefore, correlation observables constitute a powerful diagnostic tool for
disentangling $\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ NP from $\left(C_{S_{L}},C_{S_{R}}\right)$ scenarios.

Finally, among the remaining combinations, $\mathcal{K}_{1ss}$ shows strong
positive correlations with $\mathcal{K}_{2ss}$, $\mathcal{K}_{2cc}$, and
$\mathcal{K}_{2c}$ in the $\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ case, while exhibiting an
opposite trend in the $\left(C_{S_{L}},C_{S_{R}}\right)$ scenario.
Conversely, $\mathcal{K}_{1cc}$ correlates positively with
$\mathcal{K}_{2ss}$, $\mathcal{K}_{2cc}$, and $\mathcal{K}_{2c}$ for
$\left(C_{S_{L}},C_{S_{R}}\right)$ but negatively for
$\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$.
Additionally, $\mathcal{K}_{1c}$--$\mathcal{K}_{2c}$ exhibits a strong negative
correlation in the $\left(\Re\!\left[C_{S_{L}}=4C_{T}\right],
\Im\!\left[C_{S_{L}}=4C_{T}\right]\right)$ scenario, whereas
$\mathcal{K}_{2c}$--$\mathcal{K}_{4s}$ shows a strong positive correlation,
further emphasizing the distinct interference patterns and phase dependence of
the two NP scenarios.





\begin{figure}[H]
\centering 
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr12.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr13.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr14.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr15.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr16.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr17.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr18.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr19.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr1x.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr23.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr24.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr25.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr26.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr27.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr28.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr29.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr2x.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr34.pdf}
\caption{}
\end{subfigure}
\caption{\label{corr-2d}
Preferred $1\sigma$ regions for the four two-WC scenarios (listed in panel (a)),
obtained from correlation plots of the angular observables
$\mathcal{K}_{i}(q^{2})$, subject to the constraint
$\mathcal{B}(B_{c}^{-}\to\tau^{-}\bar{\nu}_{\tau})<60\%$.
The orange dashed line indicates the
$\mathcal{B}(B_{c}^{-}\to\tau^{-}\bar{\nu}_{\tau})<60\%$ bound,
while the red stars denote the SM predictions.
The legend and color scheme follow those shown in Fig.~\ref{corr-2d}(a).
}
\end{figure}

\begin{figure}[H]
\centering 
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr35.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr36.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr37.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr38.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr39.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr3x.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr45.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr46.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr47.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr48.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr49.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr4x.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr56.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr57.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr58.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr59.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr5x.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr67.pdf}
\caption{}
\end{subfigure}
\caption{\label{corr-2d-1}
 Correlation plots of the angular observables $\mathcal{K}_{i}(q^{2})$.
The legend, color coding, and conventions are the same as in
Fig.~\ref{corr-2d}.
}
\end{figure}

\begin{figure}[H]
\centering 
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr68.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr69.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr6x.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr78.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr79.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr7x.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr89.pdf}
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr8x.pdf} 
\caption{}
\end{subfigure}
\begin{subfigure}[b]{0.32\textwidth}
\centering 
\includegraphics[width=5.6cm, height=3.5cm]{corr9x.pdf}
\caption{}
\end{subfigure}

\caption{\label{corr-2d-2}
 Correlation plots of the angular observables $\mathcal{K}_{i}(q^{2})$.
The legend, color coding, and conventions are the same as in
Fig.~\ref{corr-2d}.
}
\end{figure}



\section{Conclusion}\label{sec6}

The experimental results for $R_{\tau/(\mu,e)}(D^{(*)})$ from BaBar, Belle, and LHCb show a $3.8\sigma$ deviation from SM predictions. Using the latest HFLAV results and imposing branching ratio constraints of $60\%$, $30\%$, and $10\%$ from the $B_c$ meson lifetime, we determine the WCs for various NP models. Our $\chi^2$ analysis indicates that the $(C_{V_L},C_{S_R})$ scenario achieves the highest $p$-value, $87\%$, and a maximum pull of $4.2\sigma$ from the SM predictions, demonstrating a significant improvement in fitting the data. Additionally, one-dimensional NP scenarios, $C_{V_L}$ also achieve a $p$-value of $93\%$, highlighting multiple pathways for NP contributions. NP scenarios are particularly sensitive to $B_c \to \tau \nu$ branching ratio constraints, underscoring the importance of precise measurements.

The baryonic decay $\Lambda_b \to \Lambda_c \tau \bar{\nu}_\tau$ offers a complementary avenue to explore the $R_{\tau/(\mu,e)}(D^{(*)})$ anomaly. Unlike mesonic decays, where form factors are well studied, the $\Lambda_b \to \Lambda_c$ form factors are not yet experimentally determined, requiring reliance on lattice QCD computations. After constraining the NP WCs, we investigate their impact on ten angular observables in the full five-folded cascade decay $\Lambda_b^0 \to \Lambda_c^+ (\to \Lambda^0 \pi^+) \tau^- (\to \pi^- \nu_\tau) \bar{\nu}_\tau$. Among these, $\mathcal{K}_{1c}$, $\mathcal{K}_{2ss}$, $\mathcal{K}_{2cc}$, and $\mathcal{K}_{4s}$ show the largest deviations from SM predictions, with the $(\Re[C_{S_L}=4C_T], \Im[C_{S_L}=4C_T])$ scenario producing the most pronounced shifts across the $q^2$ spectrum, while $(C_{S_L},C_{S_R})$ exhibits comparatively smaller effects.

Correlation analysis of these observables reveals distinct NP signatures. In the $(\Re[C_{S_L}=4C_T], \Im[C_{S_L}=4C_T])$ scenario, $\mathcal{K}_{1c}-\mathcal{K}_{2ss}$, $\mathcal{K}_{1c}-\mathcal{K}_{2cc}$, and $\mathcal{K}_{1c}-\mathcal{K}_{4s}$ show inverse correlations, whereas $\mathcal{K}_{2ss}-\mathcal{K}_{2cc}$ and $\mathcal{K}_{2ss}-\mathcal{K}_{4s}$ remain directly correlated, signaling destructive helicity interference and potential CP-violating phases. In contrast, the $(C_{S_L},C_{S_R})$ scenario exhibits constructive correlations consistent with CP-conserving interactions. These patterns underscore the power of correlation observables in distinguishing NP scenarios.

In summary, the baryonic decay $\Lambda_b^0 \to \Lambda_c^+ (\to \Lambda^0 \pi^+) \tau^- (\to \pi^- \nu_\tau) \bar{\nu}_\tau$ provides a unique and sensitive probe for NP, complementing mesonic $R_{\tau/(\mu,e)}(D^{(*)})$ anomalies. The angular observables $\mathcal{K}_{1c}$, $\mathcal{K}_{2ss}$, $\mathcal{K}_{2cc}$, and $\mathcal{K}_{4s}$ are particularly sensitive to $(\Re[C_{S_L}=4C_T], \Im[C_{S_L}=4C_T])$ and  $(C_{S_L},C_{S_R})$ NP effects, with distinct correlation patterns revealing possible CP-violating phases. These results establish baryonic modes as a promising laboratory for future experimental tests at LHCb Upgrade II and next-generation $b$-decay facilities.

\section*{Data Availability Statement}

%No Data associated in the manuscript.
Data sharing not applicable to this article as no datasets were generated or analysed during the current study.

\section*{Code Availability Statement}

Code/Software sharing not applicable to this article as no code/software was generated or analysed during the current study.

\appendix
\numberwithin{equation}{section}

\section{Expressions of Physical observables in terms of NP WCs}\label{AppendixA}
The expressions of the physical observables used to fit the data are given below \cite{Arslan:2023wgk}:
\begin{eqnarray}
R_{\tau/{\mu,e}}(D) & = & R_{\tau/{\mu,e}}^{\text{SM}}(D)\left\{ \left|1+\widetilde{C}_{V_{L}}+\widetilde{C}_{V_{R}}\right|^{2}+1.01\left|\widetilde{C}_{S_{L}}+\widetilde{C}_{S_{R}}\right|^{2}+0.84\left|\widetilde{C}_{T}\right|^{2}\right.\nonumber \\
 &  & \left.+1.49\Re\left[\left(1+\widetilde{C}_{V_{L}}+\widetilde{C}_{V_{R}}\right)\left(\widetilde{C}_{S_{L}}+\widetilde{C}_{S_{R}}\right)^{*}\right]+1.08\Re\left[\left(1+\widetilde{C}_{V_{L}}+\widetilde{C}_{V_{R}}\right)\left(\widetilde{C}_{T}\right)^{*}\right]\right\} ,\label{eqn1}\\
R_{\tau/{\mu,e}}(D^{*}) & = & R_{\tau/{\mu,e}}^{\text{SM}}(D^{*})\left\{ \left|1+\widetilde{C}_{V_{L}}\right|^{2}+\left|\widetilde{C}_{V_{R}}\right|^{2}+0.04\left|\widetilde{C}_{S_{L}}-\widetilde{C}_{S_{R}}\right|^{2}+16\left|\widetilde{C}_{T}\right|\right.\nonumber \\
 &  & \left.-1.83\Re\left[\left(1+\widetilde{C}_{V_{L}}\right)\left(\widetilde{C}_{V_{R}}\right)^{*}\right]-0.11\Re\left[\left(1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}\right)\left(\widetilde{C}_{S_{L}}-\widetilde{C}_{S_{R}}\right)^{*}\right]\right.\nonumber \\
 &  & \left.-5.17\Re\left[\left(1+\widetilde{C}_{V_{L}}\right)\left(\widetilde{C}_{T}\right)^{*}\right]+6.60\Re\left[\widetilde{C}_{V_{R}}\left(\widetilde{C}_{T}\right)^{*}\right]\right\} ,\label{eqn2}\\
 P_{\tau}\left(D\right) & = & P_{\tau}^{SM}\left(D\right)\left(\frac{R_{\tau/{\mu,e}}(D)}{R_{\tau/{\mu,e}}^{\text{SM}}(D)}\right)^{-1}\left\{ \left|1+\widetilde{C}_{V_{L}}\widetilde{C}_{V_{R}}\right|^{2}+3.04\left|\widetilde{C}_{S_{L}}+\widetilde{C}_{S_{R}}\right|^{2}+0.17\left|\widetilde{C}_{T}\right|^{2}\right.\nonumber \\
 &  & \left.+4.50\Re\left[\left(1+\widetilde{C}_{V_{L}}+\widetilde{C}_{V_{R}}\right)\left(\widetilde{C}_{S_{L}}+\widetilde{C}_{S_{R}}\right)^{*}\right]-1.09\Re\left[\left(1+\widetilde{C}_{V_{L}}+\widetilde{C}_{V_{R}}\right)\left(\widetilde{C}_{T}\right)^{*}\right]\right.\label{eqn8}\\
P_{\tau}\left(D^{*}\right) & = & P_{\tau}^{SM}\left(D^{*}\right)\left(\frac{R_{\tau/{\mu,e}}(D^{*})}{R_{\tau/{\mu,e}}^{\text{SM}}(D^{*})}\right)^{-1}\left\{ \left|1+\widetilde{C}_{V_{L}}\right|^{2}+\left|\widetilde{C}_{V_{R}}\right|^{2}-0.07\left|\widetilde{C}_{S_{L}}-\widetilde{C}_{S_{R}}\right|^{2}-1.85\left|\widetilde{C}_{T}\right|^{2}\right.\nonumber \\
 &  & \left.-1.79\Re\left[\left(1+\widetilde{C}_{V_{L}}\right)\left(\widetilde{C}_{V_{R}}\right)^{*}\right]+0.23\Re\left[\left(1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}\right)\left(\widetilde{C}_{S_{L}}-\widetilde{C}_{S_{R}}\right)^{*}\right]\right.\nonumber \\
 &  & \left.\left.-3.47\Re\left[\left(1+\widetilde{C}_{V_{L}}\right)\left(\widetilde{C}_{T}\right)^{*}\right]+4.41\Re\left[\widetilde{C}_{V_{R}}\left(\widetilde{C}_{T}\right)^{*}\right]\right\} \right.\label{eqn3}\\
F_{L}\left(D^{*}\right) & = & F_{L}^{SM}\left(D^{*}\right)\left(\frac{R_{\tau/{\mu,e}}(D^{*})}{R_{\tau/{\mu,e}}^{\text{SM}}(D^{*})}\right)^{-1}\left\{ \left|1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}\right|^{2}+0.08\left|\widetilde{C}_{S_{L}}-\widetilde{C}_{S_{R}}\right|^{2}+6.9\left|\widetilde{C}_{T}\right|^{2}\right.\nonumber \\
 &  & \left.\left.-0.25\Re\left[\left(1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}\right)\left(\widetilde{C}_{S_{L}}-\widetilde{C}_{S_{R}}\right)^{*}\right]-4.3\Re\left[\left(1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}\right)\left(\widetilde{C}_{T}\right)^{*}\right]\right\} \right.\label{eqn4}\\
%R_{\tau/{\mu}}(J/\psi) & = & R_{\tau/{\mu}}^{\text{SM}}(J/\psi)\left\{ \left|1+\widetilde{C}_{V_{L}}\right|^{2}+\left|\widetilde{C}_{V_{R}}\right|^{2}+0.04\left|\widetilde{C}_{S_{L}}-\widetilde{C}_{S_{R}}\right|^{2}+14.7\left|\widetilde{C}_{T}\right|^{2}\right.\nonumber \\
% &  & \left.-1.82\Re\left[\left(1+\widetilde{C}_{V_{L}}\right)\left(\widetilde{C}_{V_{R}}\right)^{*}\right]+0.1\Re\left[\left(1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}\right)\left(\widetilde{C}_{S_{L}}-\widetilde{C}_{S_{R}}\right)^{*}\right]\right.\nonumber \\
% &  & \left.-5.39\Re\left[\left(1+\widetilde{C}_{V_{L}}\right)\left(\widetilde{C}_{T}\right)^{*}\right]+6.57\Re\left[\widetilde{C}_{V_{R}}\left(\widetilde{C}_{T}\right)^{*}\right]\right\} ,\label{eqn5}
%R_{\tau/{\ell}}\left(\Lambda_{c}\right) & = & R_{\tau/{\ell}}^{\text{SM}}\left(\Lambda_{c}\right)\left\{ \left|1+\widetilde{C}_{V_{L}}\right|^{2}+\left|\widetilde{C}_{V_{R}}\right|^{2}+0.32\left(\left|\widetilde{C}_{S_{L}}\right|^{2}+\left|\widetilde{C}_{S_{R}}\right|^{2}\right)+10.4\left|\widetilde{C}_{T}\right|^{2}\right.\nonumber \\
 %&  & \left.-0.72\Re\left[\left(1+\widetilde{C}_{V_{L}}\right)\left(\widetilde{C}_{V_{R}}\right)^{*}\right]+0.5\Re\left[\left(1+\widetilde{C}_{V_{L}}\right)\left(\widetilde{C}_{S_{R}}\right)^{*}+\widetilde{C}_{V_{R}}\left(\widetilde{C}_{S_{L}}\right)^{*}\right]\right.\nonumber \\
 %&  & \left.+0.33\Re\left[\left(1+\widetilde{C}_{V_{L}}\right)\left(\widetilde{C}_{S_{L}}\right)^{*}+\widetilde{C}_{V_{R}}\left(\widetilde{C}_{S_{R}}\right)^{*}\right]+0.52\Re\left[\widetilde{C}_{S_{R}}\left(\widetilde{C}_{S_{L}}\right)^{*}\right]\right.\nonumber \\
 %&  & \left.-3.11\Re\left[\left(1+\widetilde{C}_{V_{L}}\right)\left(\widetilde{C}_{T}\right)^{*}\right]+4.88\Re\left[\widetilde{C}_{V_{R}}\left(\widetilde{C}_{T}\right)^{*}\right]\right\} \label{eqn7}
\end{eqnarray}
Similarly, the expression of branching ratio of the $B_{c}\to\tau\bar{\nu}_{\tau}$
decay read as 
\begin{eqnarray*}
\mathcal{B}\left(B_{c}^{-}\rightarrow\tau^{-}\bar{\nu}_{\tau}\right) & = & \mathcal{B}\left(B_{c}^{-}\rightarrow\tau^{-}\bar{\nu}_{\tau}\right)^{\text{SM}}\left\{ \left|1+\widetilde{C}_{V_{L}}-\widetilde{C}_{V_{R}}-4.35\left(\widetilde{C}_{S_{L}}-\widetilde{C}_{S_{R}}\right)\right|^{2}\right\} ,
\end{eqnarray*}
where in the SM $\mathcal{B}\left(B_{c}^{-}\rightarrow\tau^{-}\bar{\nu}_{\tau}\right)^{\text{SM}}\approx 0.022$  \cite{Iguro:2022yzr}.  


\section{The detailed calculation of the measurable angular distribution}\label{obsRLc}


The differential decay rate of the unpolarized $\Lambda_{b}^{0}\left(p_1,m_1\right)\rightarrow\Lambda_{c}^{+}\left(p_2,m_2\right)\left[\rightarrow\Lambda^{0}\pi^{+}\right]\tau^{-}\left(\rightarrow\pi^{-}\nu_{\tau}\right)\bar{\nu}_{\tau}$
decay can be written as:
\begin{equation}
d\Gamma=\frac{1}{2m_{1}}\left|\mathcal{M}\right|^{2}d\Pi_{5}\left(p_{1};p_{2},p_{\pi^{+}},p_{\pi^{-}},p_{\nu},p_{\bar{\nu}}\right)\label{B1}\;,
\end{equation}
where the prefactor $1/2m_{1}$ comes from relativistic flux normalization,
$\left|\mathcal{M}\right|^{2}$ encodes all the dynamics (including
spins, helicities), the matrix elements $\Lambda_b \to \Lambda_c$ transitions for various four-quark operators and their corresponding WCs. It square reads as:
\begin{align}
\left|\mathcal{M}\right|^{2} & =\sum_{\lambda_{3}}\frac{1}{2}\sum_{\lambda_{1}}\left|\mathcal{M}_{\lambda_{1}}^{\lambda_{3}}\right|^{2},\notag\\
\mathcal{M}_{\lambda_{1}}^{\lambda_{3}} & =\sum_{\lambda_{2},\lambda_{\tau}}\frac{\mathcal{M}_{\lambda_{1}}^{\lambda_{2},\lambda_{\tau}}\left(\Lambda_{b}\rightarrow\Lambda_{c}\tau\bar{\nu}_{\tau}\right)\mathcal{M}_{\lambda_{2}}^{\lambda_{3}}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right)\mathcal{M}_{\lambda_{\tau}}\left(\tau\rightarrow\pi^{-}\nu_{\tau}\right)}{\left(p_{2}^{2}-m_{2}^{2}+im_{2}\Gamma_{2}\right)\left(p_{\tau}^{2}-m_{\tau}^{2}+im_{\tau}\Gamma_{\tau}\right)}\;\label{B2}.
\end{align}
Here,  $\lambda_1$, $\lambda_2$ and $\lambda_\tau$ represent the helicities of $\Lambda_b$, $\Lambda_c$ and $\tau$, respectively.  We drop
the helicity indices $\lambda_{\pi^{\pm}}$ as they are scalars and hence they do not carry and spin. In above equation we assumed that due to the unstable nature of $\Lambda_{c}$ and $\tau$, they will decay further and act as resonances, i.e., 
%Therefore, each denominator is a Breit--Wigner propagator, and
%for a spin-\textonehalf{} particle, this connects the decay amplitude
%of a process involving unstable intermediate particles to their quantum
%field theory propagators. The corresponding decay chains will read as:
\begin{equation}
\Lambda_{c}\rightarrow\Lambda\pi^{+},\quad\tau^{-}\rightarrow\pi^{-}\nu_{\tau}\;.
\end{equation}
When a particle decays via an intermediate unstable state like $\Lambda_{c}$ or $\tau$, its amplitude contains a propagator, which accounts
for the possibility that the particle goes slightly off-shell. Each
unstable intermediate state has a Breit-Wigner propagator:
%. For a
%spin$-\sfrac{1}{2}$ fermion like $\tau$ or $\Lambda_{c}$, the scalar
%propagator factor (after spin sum) becomes
\begin{equation}
\frac{1}{p^{2}-m^{2}+im\Gamma}\;.
\end{equation}
In our case, $\Gamma_2$ and $\Gamma_\tau$ correspond to the total decay widths of $\Lambda_c$ and $\tau$, respectively. 

The five-body phase space describes the allowed kinematics
for the $5-$body final state, and this can be chopped as:
\begin{equation}
d\Pi_{5}\left(p_{1};p_{2},p_{\pi^{+}},p_{\pi^{-}},p_{\nu},p_{\bar{\nu}}\right)=\frac{dq^{2}dp_{\tau}^{2}dp_{2}^{2}}{\left(2\pi\right)^{3}}d\Pi_{2}\left(p_{1};q,p_{2}\right)d\Pi_{2}\left(p_{2};p_{3},p_{\pi^{+}}\right)d\Pi_{2}\left(q;p_{\tau},p_{\bar{\nu}}\right)d\Pi_{2}\left(p_{\tau};p_{\pi^{-}},p_{\nu}\right)\;,
\end{equation}
where, $d\Pi_{5}$ is $5-$body Lorentz-invariant phase space, integrated over the invariant mass of intermediate states, i.e., $dq^{2}$, and $dp_{\tau}^{2}$. The 
$\lambda_{x}$ stands for the helicity of the particle $x$.  As neutrinos (anti-neutrinos) are left-(right) handed in the SM, therefore, their helicities are fixed: $\lambda_{\bar{\nu}_{\tau}}\left(\lambda_{\nu_{\tau}}\right)$
to $\frac{1}{2}\left(-\frac{1}{2}\right)$. These are not summed over because
they are dictated by the structure of the $V-A$ in the weak-interactions.

For a given WEH, one can express the helicity
amplitude of $\Lambda_{b}\rightarrow\Lambda_{c}\tau\bar{\nu}_{\tau}$
decay as:
\begin{equation}
\mathcal{M}_{\lambda_{1}}^{\lambda_{2},\lambda_{\tau}}\left(\Lambda_{b}\rightarrow\Lambda_{c}\tau\bar{\nu}_{\tau}\right)=\sqrt{2}G_{F}V_{cb}\left(H_{\lambda_{1}}^{\lambda_{2}}L^{\lambda_{\tau}}+\sum\eta_{\lambda}H_{\lambda_{1}}^{\lambda_{2},\lambda}L_{\lambda}^{\lambda_{\tau}}+\sum\eta_{\lambda}\eta_{\lambda^{'}}H_{\lambda_{1}}^{\lambda_{2},\lambda,\lambda^{'}}L_{\lambda,\lambda^{'}}^{\lambda_{\tau}}\right).
\end{equation}
Here, $\lambda^{\left(\prime\right)}=t,\pm1,0$ indicates the
helicity of the virtual vector boson $W^{*}$. The number of helicity
indices depends on the Lorentz structure of the effective operator.
The factor $\eta$ that appears here is due to the use of the completeness
relation of the polarization vectors of the virtual vector boson.
The hadronic and leptonic helicity amplitudes are, respectively, defined
as
\begin{eqnarray}
H_{\lambda_{1}}^{\lambda_{2}} & =&\left\langle \Lambda_{c}\left(\lambda_{2}\right)\left|g_{S}\left(\bar{c}b\right)+g_{P}\left(\bar{c}\gamma_{5}b\right)\right|\Lambda_{b}\left(\lambda_{1}\right)\right\rangle ,\notag\\
H_{\lambda_{1}}^{\lambda_{2},\lambda} & =&\epsilon^{\mu*}\left(\lambda\right)\left\langle \Lambda_{c}\left(\lambda_{2}\right)\left|g_{V}\left(\bar{c}\gamma_{\mu}b\right)+g_{A}\left(\bar{c}\gamma_{\mu}\gamma_{5}b\right)\right|\Lambda_{b}\left(\lambda_{1}\right)\right\rangle ,\notag\\
H_{\lambda_{1}}^{\lambda_{2},\lambda,\lambda^{\prime}} & =&g_{T}\epsilon^{\mu*}\left(\lambda\right)\epsilon^{\nu*}\left(\lambda^{\prime}\right)\left\langle \Lambda_{c}\left(\lambda_{2}\right)\left|\bar{c}i\sigma_{\mu\nu}\gamma_{\mu}\left(1-\gamma_{5}\right)b\right|\Lambda_{b}\left(\lambda_{1}\right)\right\rangle ,
\end{eqnarray}
and
\begin{eqnarray}
L^{\lambda_{\tau}} & =&\left\langle \tau^{-}\left(\lambda_{\tau}\right)\bar{\nu}\left|\tau P_{L}\nu\right|0\right\rangle ,\notag\\
L_{\lambda}^{\lambda_{\tau}} & =&\epsilon^{\mu}\left(\lambda\right)\left\langle \tau^{-}\left(\lambda_{\tau}\right)\bar{\nu}\left|\tau\gamma_{\mu}P_{L}\nu\right|0\right\rangle ,\notag\\
L_{\lambda,\lambda^{\prime}}^{\lambda_{\tau}} & =&\left(-i\right)\epsilon^{\mu}\left(\lambda\right)\epsilon^{\nu}\left(\lambda^{\prime}\right)\left\langle \tau^{-}\left(\lambda_{\tau}\right)\bar{\nu}\left|\tau\sigma_{\mu\nu}P_{L}\nu\right|0\right\rangle ,
\end{eqnarray}
where $\epsilon^{\mu}\left(\lambda\right)$ is the polarization vector
of the virtual vector boson with helicity $\lambda$ and $P_L = \frac{1}{2}\left(1-\gamma_5\right)$ and $P_L = \frac{1}{2}\left(1+\gamma_5\right)$.

Using the narrow width $\left(\Gamma_{a}\ll m_{a}\right)$ approximation
\begin{equation}
\frac{1}{\left(p_{a}^{2}-m_{a}^{2}\right)^{2}+im_{a}^{2}\Gamma_{a}^{2}}=\frac{\pi}{m_{a}\Gamma_{a}}\delta\left(p_{a}^{2}-m_{a}^{2}\right),\quad\left(a=\Lambda_{c},\tau\right)
\end{equation}
and integrating over $dp_{2}^{2}dp_{\tau}^{2}$, one can obtain
two on-shell relations $p_{2}^{2}=m_{2}^{2}$ and $p_{\tau}^{2}=m_{\tau}^{2}$,
as well as 
\begin{eqnarray}
d\Gamma & =&\frac{dq^{2}}{2^{5}\pi m_{1}m_{2}\Gamma_{2}m_{\tau}\Gamma_{\tau}}d\Pi_{2}\left(p_{1};q,p_{2}\right)d\Pi_{2}\left(p_{2};p_{3},p_{\pi^{+}}\right)d\Pi_{2}\left(q;p_{\tau},p_{\bar{\nu}}\right)d\Pi_{2}\left(p_{\tau};p_{\pi^{-}},p_{\nu}\right)\notag\\
 & \times&\sum_{\lambda_{1},\lambda_{3}}\left|\sum_{\lambda_{2},\lambda_{\tau}}\mathcal{M}_{\lambda_{1}}^{\lambda_{2},\lambda_{\tau}}\left(\Lambda_{b}\rightarrow\Lambda_{c}\tau\bar{\nu}_{\tau}\right)\mathcal{M}_{\lambda_{2}}^{\lambda_{3}}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right)\mathcal{M}_{\lambda_{\tau}}\left(\tau\rightarrow\pi^{-}\nu_{\tau}\right)\right|^{2}.
\end{eqnarray}
Since each individual two-body phase space or helicity amplitude is
Lorentz invariant, one can calculate each part of $d\Gamma$ in different
reference frames. In this work, we should consider three measurable
reference frames -- the $\Lambda_{b}$ rest frame, the $\Lambda_{c}$
rest frame and the $\tau^{-}\bar{\nu}_{\tau}$ center-of-mass frame. 

\subsection{$\Lambda_{b}$ rest frame}

In the $\Lambda_{b}$ rest frame, we calculate the hadronic helicity amplitudes
$H$ and the two-body phase space $d\Pi_{2}\left(p_{1};q,p_{2}\right)$.
The momenta of $\Lambda_{b}$, $\Lambda_{c}$ and $W^{*}$ are respectively
as
\begin{equation}
p_{1}^{\mu}=\left(m_{1},0,0,0\right),\quad p_{2}^{\mu}=\left(E_{2},0,0,\left|\bf{q}\right|\right),\quad q^{\mu}=\left(q_{0},0,0,-\left|\bf{q}\right|\right)
\end{equation}
By the virtue of the Lorentz condition $q_{\mu}\epsilon^{\mu}=0$,  the polarization
vector of virtual boson becomes
\begin{eqnarray}
\epsilon^{\mu}\left(t\right) & =&\frac{1}{\sqrt{q^{2}}}\left(q^{0},0,0,q^{3}\right)=\frac{1}{\sqrt{q^{2}}}\left(q_{0},0,0,-\left|\bf{q}\right|\right),\notag\\
\epsilon^{\mu}\left(0\right) & =&\frac{1}{\sqrt{q^{2}}}\left(-q^{3},0,0,q^{0}\right)=\frac{1}{\sqrt{q^{2}}}\left(\left|\bf{q}\right|,0,0,-q_{0}\right),\notag\\
\epsilon^{\mu}\left(\pm1\right) & =&\frac{1}{\sqrt{2}}\left(0,\pm1,i,0\right).
\end{eqnarray}

The spinors of $\Lambda_{b}$ and $\Lambda_{c}$ are described by
the Dirac spinors $u\left(p,s\right)$, which satisfies the Dirac equation. 
\begin{equation}
\left(\slashed{p}-m\right)u\left(p,s\right)=0,
\end{equation}
where $p^{\mu}$, $m$ are the four-momentum and mass of the baryon, $u\left(p,s\right)$
is a four-component spinor corresponding to a specific helicity $s$.

In the rest frame of $\Lambda_{b}$, its spinor reads as 
\begin{equation}
u_{1}\left(p_{1},s\right)=\sqrt{2m_{1}}\left(\begin{array}{c}
\chi_{s}\\
0
\end{array}\right). 
\end{equation}
The corresponding
spinors of $\Lambda_{c}$ is then
\[
u_{2}\left(p_{2},s\right)=\left(\begin{array}{c}
\beta_{2}^{+}\chi_{s}\\
\pm\beta_{2}^{-}\chi_{s}
\end{array}\right),\beta_{x}^{\pm}=\sqrt{E_{x}\pm m_{x}}\;.
\]
Also
\[
\bar{u}_{2}\left(p_{2},s\right)=u_{2}^{\dagger}\gamma^{0}=\left(\begin{array}{cc}
\beta_{2}^{+}\chi_{s} & \pm\beta_{2}^{-}\chi_{s}\end{array}\right)\left(\begin{array}{cc}
I & 0\\
0 & -I
\end{array}\right)=\left(\begin{array}{cc}
\beta_{2}^{+}\chi_{s}^{\dagger} & \mp\beta_{2}^{-}\chi_{s}^{\dagger}\end{array}\right)\;,
\]
and 
\[
\left|q\right|=\frac{\lambda^{1/2}\left(m_{1}^{2},m_{2}^{2},q^{2}\right)}{2m_{1}},\quad E_{2}=\frac{m_{1}^{2}+m_{2}^{2}-q^{2}}{2m_{1}},
\]
where K$\ddot{a}$llen function $\lambda\left(a,b,c\right)\equiv a^{2}+b^{2}+c^{2}-2ab-2bc-2ca$,
implies
\[
\lambda^{1/2}\left(m_{1}^{2},m_{2}^{2},q^{2}\right)=Q_{+}Q_{-},\quad Q_{\pm}=\left(m_{1}\pm m_{2}\right)^{2}-q^{2}.
\]

Most generally, the $n-$body phase space is defined as 
\begin{equation}
d\Pi_{n}\left(P,p_{i}\right)=\left(\Pi_{i}\frac{d^{3}p_{i}}{\left(2\pi\right)^{3}2E_{i}}\right)\left(2\pi\right)^{4}\delta^{\left(4\right)}\left(P-\sum p_{i}\right)\label{B14},
\end{equation}
and the corresponding two-body phase space  $d\Pi_{2}\left(p_{1};q,p_{2}\right)$ has the form \cite{ParticleDataGroup:2024cfk}

\[
d\Pi_{2}\left(p_{1};q,p_{2}\right)=\frac{1}{4\pi}\frac{\left|\textbf{q}\right|}{m_{1}},
\]
with $\left|\textbf{q}\right|=\frac{1}{2m_{1}}\sqrt{\lambda\left(m_{1}^{2},m_{2}^{2},q^{2}\right)}$,
$E_{2}=\frac{1}{2m_{1}}\left(m_{1}^{2}+m_{2}^{2}-q^{2}\right)$, $q_{0}=\frac{1}{2m_{1}}\left(m_{1}^{2}-m_{2}^{2}+q^{2}\right)$
and $\lambda\left(m_{1}^{2},m_{2}^{2},q^{2}\right)=Q_{+}Q_{-}.$ 


\subsection{$\Lambda_{c}$ rest frame}

In the $\Lambda_{c}$ rest frame, we calculate helicity amplitude
$\mathcal{M}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right)$ and
two-body phase space $d\Pi_{2}\left(p_{2};p_{3},p_{\pi^{+}}\right)$.
The momenta of $\Lambda_{c}$ and $\Lambda$ are respectively as
\[
\tilde{p}_{2}^{\mu}=\left(m_{2},0,0,0\right),\quad p_{3}^{\mu}=\left(E_{3},\left|\textbf{p}_{3}\right|\sin\theta_{3},0,\left|\textbf{p}_{3}\right|\cos\theta_{3}\right).
\]
The tilde over the momenta are only used to distinguish the representations
of the same kinematic quantity in different reference frames. The
spinors of $\Lambda_{c}$ and $\Lambda$ are given by:
\[
u\left(p,s\right)=\sqrt{E+m}\left(\begin{array}{c}
\chi_{s}\\
\frac{\bf{\sigma}\cdot \bf{p}}{E+m}\chi_{s}
\end{array}\right),
\]

\begin{align*}
u_{3}\left(p_{3},\frac{1}{2}\right) & =\left(\begin{array}{cccc}
\beta_{3}^{+}\cos\left(\frac{\theta_{3}}{2}\right), & \beta_{3}^{+}\sin\left(\frac{\theta_{3}}{2}\right), & \beta_{3}^{-}\cos\left(\frac{\theta_{3}}{2}\right), & \beta_{3}^{-}\sin\left(\frac{\theta_{3}}{2}\right)\end{array}\right)^{T},\\
u_{3}\left(p_{3},-\frac{1}{2}\right) & =\left(\begin{array}{cccc}
-\beta_{3}^{+}\sin\left(\frac{\theta_{3}}{2}\right), & \beta_{3}^{+}\cos\left(\frac{\theta_{3}}{2}\right), & \beta_{3}^{-}\sin\left(\frac{\theta_{3}}{2}\right), & -\beta_{3}^{-}\cos\left(\frac{\theta_{3}}{2}\right)\end{array}\right)^{T}.
\end{align*}
The corresponding two-body phase space is then
\begin{equation}
d\Pi_{2}\left(p_{2};p_{3},p_{\pi^{+}}\right)=\frac{1}{8\pi}\frac{\left|\textbf{p}_{3}\right|}{E_{3}+E_{\pi^{+}}}d\cos\theta_{3}=\frac{1}{8\pi}\frac{\left|\textbf{p}_{3}\right|}{m_{2}}d\cos\theta_{3},
\end{equation}
with
\begin{align*}
\left|p_{3}\right| & =\frac{1}{2m_{2}}\lambda^{1/2}\left(m_{2}^{2},m_{3}^{2},m_{\pi^{+}}^{2}\right)=p^{*},\\
E_{3} & =\frac{1}{2m_{2}}\left(m_{2}^{2}+m_{3}^{2}-m_{\pi^{+}}^{2}\right).
\end{align*}

Now, as the pion is a pseudoscalar (spin-0, odd parity),  the only allowed Lorentz scalars (respecting parity) are
$\bar{u}u$ and $\bar{u}\gamma^{5}u$. So, the helicity amplitude becomes
\begin{equation}
\mathcal{M}_{\lambda_{2}}^{\lambda_{3}}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right)=i\bar{u}_{3}\left(\lambda_{3}\right)\left(A+B\gamma_{5}\right)u_{2}\left(\lambda_{2}\right)\;.
\end{equation}
This describes a scalar--pseudoscalar structure, where $A$: scalar
coupling (parity conserving), $B$: pseudoscalar coupling (parity violating). This is a valid low-energy hadronic parameterization of the weak decay
$\Lambda_{c}\rightarrow\Lambda\pi^{+}$


\begin{equation}
\mathcal{M}_{\lambda_{2}}^{\lambda_{3}}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right)=i\chi_{s}^{\dagger}\left(\lambda_{3}\right)\left(S+P\bf{\sigma}.\hat{p}_{3}\right)\chi_{s}\left(\lambda_{2}\right)\;,
\end{equation}
where $S=\sqrt{2m_{2}}\beta_{3}^{+}$ and $P=-\sqrt{2m_{2}}\beta_{3}^{-}$. $\bf{\sigma}=\left(\begin{array}{ccc}
\sigma^{1}, & \sigma^{2}, & \sigma^{3}\end{array}\right)$ is a vector composed of Pauli matrices. $\hat{p}_{3}$ is the unit
vector along the direction of $\Lambda$ baryon. The four helicity
amplitudes are:
\begin{align*}
\mathcal{M}_{1/2}^{1/2}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right)  =i\left(S+P\right)\cos\left(\frac{\theta_{3}}{2}\right),\quad\mathcal{M}_{-1/2}^{1/2}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right) =i\left(S+P\right)\sin\left(\frac{\theta_{3}}{2}\right),
\end{align*}
\begin{align}
\mathcal{M}_{1/2}^{-1/2}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right) =-i\left(S-P\right)\sin\left(\frac{\theta_{3}}{2}\right),\quad\mathcal{M}_{-1/2}^{1/2}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right) =i\left(S-P\right)\cos\left(\frac{\theta_{3}}{2}\right)\;.
\end{align}
For a two body decay $\Lambda_{c}\rightarrow\Lambda\pi^{+}$
\begin{equation}
\Gamma^{\lambda_{3}=1/2}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right)=\frac{\left|\textbf{p}_{3}\right|}{8\pi m_{3}^{2}}\frac{1}{2}\left|\mathcal{M}^{1/2}\right|^{2}\;.
\end{equation}
The factor of $\frac{1}{2}$ comes from averaging over the initial $\Lambda_{c}$
spin. Therefore
\begin{equation}
\Gamma^{\lambda_{3}=1/2}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right)=\frac{\left|\textbf{p}_{3}\right|}{16\pi m_{3}^{2}}\left|S+P\right|^{2}\;.
\end{equation}
In the same way, one can obtain the decay rate for helicity $\lambda_{3}=-1/2$:
\begin{equation}
\Gamma^{\lambda_{3}=-1/2}\left(\Lambda_{c}\rightarrow\Lambda\pi^{+}\right)=\frac{\left|\textbf{p}_{3}\right|}{16\pi m_{3}^{2}}\left|S-P\right|^{2}\;.
\end{equation}
By using the two helicity amplitudes, the angular asymmetry parameter has the form
$\alpha_{\Lambda_{c}}$ has the form
\begin{equation}
\alpha_{\Lambda_{c}}=\frac{2\Re\left(S^{*}P\right)}{\left|S\right|^{2}+\left|P\right|^{2}},
\end{equation}
and one can immediately get the relations
\begin{align*}
\frac{\Gamma^{\lambda_{3}=1/2}}{\Gamma^{\lambda_{3}=1/2}+\Gamma^{\lambda_{3}=-1/2}} & =\frac{\left|S+P\right|^{2}}{\left|S+P\right|^{2}+\left|S-P\right|^{2}}\\
 & =\frac{1}{2}\left(1+\alpha_{\Lambda_{c}}\right)\;.
\end{align*}
Similarly
\[
\frac{\Gamma^{\lambda_{3}=-1/2}}{\Gamma^{\lambda_{3}=1/2}+\Gamma^{\lambda_{3}=-1/2}}=\frac{1}{2}\left(1-\alpha_{\Lambda_{c}}\right).
\]


\subsection{$\tau^{-}\bar{\nu}_{\tau}-$ center of mass frame}
In this frame, we calculate the leptonic helicity amplitudes $L$
and the helicity amplitudes $\mathcal{M}_{\lambda_{\tau}}\left(\tau^-\to\pi^{-}\nu_{\tau}\right)$,
as well as the two-body phase spaces $d\Pi_{2}\left(q;p_{\tau},p_{\bar{\nu}}\right)$
and $d\Pi_{2}\left(p_{\tau};p_{\pi^{-}},p_{\nu}\right)$. The momenta
of $\pi^{-}$ is defined as $p_{\pi}=\left(E_{\pi},\left|\textbf{p}_{\pi}\right|\hat{p}_{\pi}\right)$
with
\[
\hat{p}_{\pi}=\left(\sin\theta_{\pi}\cos\phi_{\pi},\sin\theta_{\pi}\sin\phi_{\pi},\cos\theta_{\pi}\right),
\]
is the unit vector along the direction of $\pi^{-}$. In this frame,
the polarization vectors of the virtual vector boson $W^{*}$ are
changed to 
\[
\tilde{\epsilon}^{\mu}\left(t\right)=\left(1,0,0,0\right),\quad\tilde{\epsilon}^{\mu}\left(\pm1\right)=\frac{1}{\sqrt{2}}\left(0,\pm1,-i,0\right),\quad\tilde{\epsilon}^{\mu}\left(0\right)=\left(0,0,0,-1\right)\;.
\]
Because $W^{*}$ is at rest in this frame, $4-$momentum of $W^{*}$ is
$q^{\mu}=\left(q^{0},\textbf{0}\right)=\left(\sqrt{q^{2}},0,0,0\right)$. Also, 
a massive vector boson (virtual $W^{*}$) has $4-$polarization states,
$1$ time-like/unphysical $\lambda=t$ and $3$ physical $\lambda=\pm1,0$.
For time like polarization, we can write
\[
\epsilon^{\mu}\left(t\right)=\frac{1}{\sqrt{q^{2}}}\left(q^{0},\textbf{0}\right)=\frac{1}{\sqrt{q^{2}}}\left(\sqrt{q^{2}},\textbf{0}\right)=\left(1,0,0,0\right)\;.
\]
This component is not physical for a real gauge bosons, but appears in
virtual processes like off-shell $W^{*}\rightarrow\tau^{-}\bar{\nu}_{\tau}$,
especially in the leptonic tensor decomposition. For physical polarizations,
the Lorentz condition holds: $q_{\mu}\epsilon^{\mu}\left(\lambda\right)=0$.
For $\lambda=t$, this gives 
\[
q_{\mu}\epsilon^{\mu}\left(t\right)=\sqrt{q^{2}}\neq0.
\]
Transverse polarization: $\tilde{\epsilon}^{\mu}\left(\pm1\right)=\frac{1}{\sqrt{2}}\left(0,\pm1,-i,0\right),$
represent circularly polarized states in the $xy$-plane, and longitudinal
polarizaion: $\tilde{\epsilon}^{\mu}\left(0\right)=\left(0,0,0,-1\right),$ this
points along the $-z$ axis. For transverse case, we can write
\[
q_{\mu}\epsilon^{\mu}\left(\pm1,0\right)=0.
\]

The helicity amplitudes $\mathcal{M}_{\lambda_{\tau}}\left(\tau^-\to\pi^{-}\nu_{\tau}\right)$
can be written as 
\begin{equation}
\mathcal{M}_{\lambda_{\tau}}\left(\tau^-\to\pi^{-}\nu_{\tau}\right)=i\sqrt{2}G_{F}V_{ud}^{*}f_{\pi}u_{\bar{\nu}_{\tau}}\cancel{p}_{\pi}P_{L}u_{\tau}\left(\lambda_{\tau}\right)\;.
\end{equation}
In the case of low-energy effective Lagrangian
\begin{equation}
\mathcal{L}_{eff}=\frac{G_{F}}{\sqrt{2}}V_{ud}\left[\bar{u}\gamma^{\mu}\left(1-\gamma_{5}\right)d\right]\left[\bar{\nu}_{\tau}\gamma_{\mu}\left(1-\gamma_{5}\right)\tau\right],
\end{equation}
using hadronization of the quark current, the hadronic matrix element
$\left\langle 0\left|\bar{u}\gamma^{\mu}\left(1-\gamma_{5}\right)d\right|\pi^{-}\left(p_{\pi}\right)\right\rangle$ becomes
\begin{equation}
\left\langle 0\left|\bar{u}\gamma^{\mu}\gamma_{5}d\right|\pi^{-}\left(p_{\pi}\right)\right\rangle =if_{\pi}p_{\pi}^{\mu}\;,
\end{equation}
where $f_{\pi}$ is the $\pi$-decay constant.
Using the effective Lagrangian and the above hadronic matrix element,
the full amplitude is
\begin{align}
\mathcal{M}_{\lambda_{\tau}} & =\left(-\frac{G_{F}}{\sqrt{2}}V_{ud}\right)\left(if_{\pi}p_{\pi}^{\mu}\right)\left[\bar{u}_{\nu_{\tau}}\gamma_{\mu}\left(1-\gamma_{5}\right)u_{\tau}\right]=-i\frac{G_{F}}{\sqrt{2}}V_{ud}f_{\pi}\left[\bar{u}_{\nu_{\tau}}\left(\gamma_{\mu}p_{\pi}^{\mu}\right)\left(2P_{L}\right)u_{\tau}\right],\notag\\
 & =i\sqrt{2}G_{F}V_{ud}^{*}f_{\pi}\left[\bar{u}_{\nu_{\tau}}\cancel{p}_{\pi}P_{L}u_{\tau}\left(\lambda_{\tau}\right)\right]\;.
\end{align}
The corresponding decay rate is then
\begin{equation}
\Gamma\left(\tau^-\to\pi^{-}\nu_{\tau}\right)=\frac{G_{F}^{2}\left|V_{ud}\right|^{2}f_{\pi}^{2}\left(m_{\tau}^{2}-m_{\pi}^{2}\right)^{2}}{16\pi m_{\tau}}\;.
\end{equation}

\begin{thebibliography}{10}

\bibitem{Arbey:2021gdg}
A.~Arbey and F.~Mahmoudi,
%``Dark matter and the early Universe: a review,''
Prog. Part. Nucl. Phys. \textbf{119}, 103865 (2021)
doi:10.1016/j.ppnp.2021.103865
[arXiv:2104.11488 [hep-ph]].
%189 citations counted in INSPIRE as of 14 Sep 2024

\bibitem{Gonzalez-Garcia:2022pbf}
M.~C.~Gonzalez-Garcia,
%``Neutrino physics,''
CERN Yellow Rep. School Proc. \textbf{5}, 85 (2022)
doi:10.23730/CYRSP-2021-005.85
%4 citations counted in INSPIRE as of 14 Sep 2024
%1
\bibitem{LHCb:2014cxe} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Differential branching fractions and isospin asymmetries of $B \to K^{(*)} \mu^+ \mu^-$ decays,''
JHEP \textbf{06}, 133 (2014) doi:10.1007/JHEP06(2014)133 {[}arXiv:1403.8044
{[}hep-ex{]}{]}.
%2
\bibitem{LHCb:2014auh} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Angular analysis of charged and neutral $B \to K \mu^+\mu^-$  decays,''
JHEP \textbf{05}, 082 (2014) doi:10.1007/JHEP05(2014)082 {[}arXiv:1403.8045
{[}hep-ex{]}{]}.
%3
\bibitem{LHCb:2015wdu} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Angular analysis and differential branching fraction of the decay $B^0_s\to\phi\mu^+\mu^-$,''
JHEP \textbf{09}, 179 (2015) doi:10.1007/JHEP09(2015)179 {[}arXiv:1506.08777
{[}hep-ex{]}{]}.
%4
\bibitem{LHCb:2015svh} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Angular analysis of the $B^{0} \to K^{*0} \mu^{+} \mu^{-}$ decay using 3 fb$^{-1}$ of integrated luminosity,''
JHEP \textbf{02}, 104 (2016) doi:10.1007/JHEP02(2016)104 {[}arXiv:1512.04442
{[}hep-ex{]}{]}.
%5
\bibitem{LHCb:2016ykl} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Measurements of the S-wave fraction in $B^{0}\rightarrow K^{+}\pi^{-}\mu^{+}\mu^{-}$ decays and the $B^{0}\rightarrow K^{\ast}(892)^{0}\mu^{+}\mu^{-}$ differential branching fraction,''
JHEP \textbf{11}, 047 (2016) {[}erratum: JHEP \textbf{04}, 142 (2017){]}
doi:10.1007/JHEP11(2016)047 {[}arXiv:1606.04731 {[}hep-ex{]}{]}.
%6
\bibitem{LHCb:2021zwz} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Branching Fraction Measurements of the Rare $B^0_s\rightarrow\phi\mu^+\mu^-$ and $B^0_s\rightarrow f_2^\prime(1525)\mu^+\mu^-$- Decays,''
Phys. Rev. Lett. \textbf{127}, no.15, 151801 (2021) doi:10.1103/PhysRevLett.127.151801
{[}arXiv:2105.14007 {[}hep-ex{]}{]}.
%7
\bibitem{LHCb:2021xxq} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Angular analysis of the rare decay $ {B}_s^0 $\textrightarrow{} \ensuremath{\phi}\ensuremath{\mu}$^{+}$\ensuremath{\mu}$^{−}$,''
JHEP \textbf{11}, 043 (2021) doi:10.1007/JHEP11(2021)043 {[}arXiv:2107.13428
{[}hep-ex{]}{]}.
%8


\bibitem{LHCb:2022vje}
R.~Aaij \textit{et al.} [LHCb],
%``Measurement of lepton universality parameters in $B^+\to K^+\ell^+\ell^-$ and $B^0\to K^{*0}\ell^+\ell^-$ decays,''
Phys. Rev. D \textbf{108}, no.3, 032002 (2023)
doi:10.1103/PhysRevD.108.032002
[arXiv:2212.09153 [hep-ex]].
%220 citations counted in INSPIRE as of 14 Sep 2024



\bibitem{LHCb:2022qnv}
R.~Aaij \textit{et al.} [LHCb],
%``Test of lepton universality in $b \rightarrow s \ell^+ \ell^-$ decays,''
Phys. Rev. Lett. \textbf{131}, no.5, 051803 (2023)
doi:10.1103/PhysRevLett.131.051803
[arXiv:2212.09152 [hep-ex]].
%231 citations counted in INSPIRE as of 14 Sep 2024


\bibitem{Smith:2024xgo}
M.~Smith [LHCb],
%``$b\to{}s\ell\ell$ decays at LHCb,''
[arXiv:2405.11890 [hep-ex]].
%2 citations counted in INSPIRE as of 14 Sep 2024


\bibitem{CMS:2024syx}
A.~Hayrapetyan \textit{et al.} [CMS],
%``Test of lepton flavor universality in B$^{\pm}$$\to$ K$^{\pm}\mu^+\mu^-$ and B$^{\pm}$$\to$ K$^{\pm}$e$^+$e$^-$ decays in proton-proton collisions at $\sqrt{s}$ = 13 TeV,''
Rept. Prog. Phys. \textbf{87}, no.7, 077802 (2024)
doi:10.1088/1361-6633/ad4e65
[arXiv:2401.07090 [hep-ex]].
%24 citations counted in INSPIRE as of 14 Sep 2024
\bibitem{Celis:2017doq} A.~Celis, J.~Fuentes-Martin, A.~Vicente
and J.~Virto, %``Gauge-invariant implications of the LHCb measurements on lepton-flavor nonuniversality,''
Phys. Rev. D \textbf{96}, no.3, 035026 (2017) doi:10.1103/PhysRevD.96.035026
{[}arXiv:1704.05672 {[}hep-ph{]}{]}.
%9
\bibitem{Buttazzo:2017ixm} D.~Buttazzo, A.~Greljo, G.~Isidori
and D.~Marzocca, %``B-physics anomalies: a guide to combined explanations,''
JHEP \textbf{11}, 044 (2017) doi:10.1007/JHEP11(2017)044 {[}arXiv:1706.07808
{[}hep-ph{]}{]}.
%10
\bibitem{Aebischer:2019mlg} J.~Aebischer, W.~Altmannshofer, D.~Guadagnoli,
M.~Reboud, P.~Stangl and D.~M.~Straub, %``$B$-decay discrepancies after Moriond 2019,''
Eur. Phys. J. C \textbf{80}, no.3, 252 (2020) doi:10.1140/epjc/s10052-020-7817-x
{[}arXiv:1903.10434 {[}hep-ph{]}{]}.
%11
\bibitem{Alasfar:2020mne} L.~Alasfar, A.~Azatov, J.~de Blas, A.~Paul
and M.~Valli, %``$B$ anomalies under the lens of electroweak precision,''
JHEP \textbf{12}, 016 (2020) doi:10.1007/JHEP12(2020)016 {[}arXiv:2007.04400
{[}hep-ph{]}{]}.
%12
\bibitem{Isidori:2021tzd} G.~Isidori, D.~Lancierini, A.~Mathad,
P.~Owen, N.~Serra and R.~Silva Coutinho, %``A general effective field theory description of b%\textrightarrow{}s\ensuremath{\ell}+\ensuremath{\ell}\ensuremath{-} lepton universality ratios,''
Phys. Lett. B \textbf{830}, 137151 (2022) doi:10.1016/j.physletb.2022.137151
{[}arXiv:2110.09882 {[}hep-ph{]}{]}.
%13
\bibitem{Ciuchini:2022wbq} M.~Ciuchini, M.~Fedele, E.~Franco,
A.~Paul, L.~Silvestrini and M.~Valli, %``Constraints on lepton universality violation from rare B decays,''
Phys. Rev. D \textbf{107}, no.5, 055036 (2023) doi:10.1103/PhysRevD.107.055036
{[}arXiv:2212.10516 {[}hep-ph{]}{]}. %1
%14
%
\bibitem{Hiller:2003js}
G.~Hiller and F.~Kruger,
%``More model-independent analysis of $b \to s$ processes,''
Phys. Rev. D \textbf{69}, 074020 (2004)
doi:10.1103/PhysRevD.69.074020
[arXiv:hep-ph/0310219 [hep-ph]].
%587 citations counted in INSPIRE as of 14 Sep 2024


%
\bibitem{Bordone:2016gaq}
M.~Bordone, G.~Isidori and A.~Pattori,
%``On the Standard Model predictions for $R_K$ and $R_{K^*}$,''
Eur. Phys. J. C \textbf{76}, no.8, 440 (2016)
doi:10.1140/epjc/s10052-016-4274-7
[arXiv:1605.07633 [hep-ph]].
%546 citations counted in INSPIRE as of 14 Sep 2024

%
\bibitem{Mishra:2020orb}
D.~Mishra and N.~Mahajan,
%``Impact of soft photons on $B\rightarrow K \ell^+ \ell^-$,''
Phys. Rev. D \textbf{103}, no.5, 056022 (2021)
doi:10.1103/PhysRevD.103.056022
[arXiv:2010.10853 [hep-ph]].
%9 citations counted in INSPIRE as of 14 Sep 2024

%
\bibitem{Isidori:2020acz}
G.~Isidori, S.~Nabeebaccus and R.~Zwicky,
%``QED corrections in $ \overline{B}\to \overline{K}{\mathrm{\ell}}^{+}{\mathrm{\ell}}^{-} $ at the double-differential level,''
JHEP \textbf{12}, 104 (2020)
doi:10.1007/JHEP12(2020)104
[arXiv:2009.00929 [hep-ph]].
%106 citations counted in INSPIRE as of 14 Sep 2024

%
\bibitem{Bernlochner:2021vlv}
F.~U.~Bernlochner, M.~F.~Sevilla, D.~J.~Robinson and G.~Wormser,
%``Semitauonic b-hadron decays: A lepton flavor universality laboratory,''
Rev. Mod. Phys. \textbf{94}, no.1, 015003 (2022)
doi:10.1103/RevModPhys.94.015003
[arXiv:2101.08326 [hep-ex]].
%69 citations counted in INSPIRE as of 15 Sep 2024


\bibitem{Fischer:2021sqw}
O.~Fischer, B.~Mellado, S.~Antusch, E.~Bagnaschi, S.~Banerjee, G.~Beck, B.~Belfatto, M.~Bellis, Z.~Berezhiani and M.~Blanke, \textit{et al.}
%``Unveiling hidden physics at the LHC,''
Eur. Phys. J. C \textbf{82}, no.8, 665 (2022)
doi:10.1140/epjc/s10052-022-10541-4
[arXiv:2109.06065 [hep-ph]].
%68 citations counted in INSPIRE as of 15 Sep 2024


\bibitem{London:2021lfn}
D.~London and J.~Matias,
%``$B$ Flavour Anomalies: 2021 Theoretical Status Report,''
Ann. Rev. Nucl. Part. Sci. \textbf{72}, 37-68 (2022)
doi:10.1146/annurev-nucl-102020-090209
[arXiv:2110.13270 [hep-ph]].
%99 citations counted in INSPIRE as of 15 Sep 2024

\bibitem{Crivellin:2021sff}
A.~Crivellin and M.~Hoferichter,
%``Hints of lepton flavor universality violations,''
Science \textbf{374}, no.6571, 1051 (2021)
doi:10.1126/science.abk2450
[arXiv:2111.12739 [hep-ph]].
%39 citations counted in INSPIRE as of 15 Sep 2024


%\cite{Crivellin:2022qcj}
\bibitem{Crivellin:2022qcj}
A.~Crivellin and J.~Matias,
%``Beyond the Standard Model with Lepton Flavor Universality Violation,''
[arXiv:2204.12175 [hep-ph]].
%13 citations counted in INSPIRE as of 15 Sep 2024



\bibitem{BaBar:2012obs} J.~P.~Lees \textit{et al.} {[}BaBar{]},
%``Evidence for an excess of $\bar{B} \to D^{(*)} \tau^-\bar{\nu}_\tau$ decays,''
Phys. Rev. Lett. \textbf{109}, 101802 (2012) doi:10.1103/PhysRevLett.109.101802
{[}arXiv:1205.5442 {[}hep-ex{]}{]}.

%25

\bibitem{BaBar:2013mob} J.~P.~Lees \textit{et al.} {[}BaBar{]},
%``Measurement of an Excess of $\bar{B} \to D^{(*)}\tau^- \bar{\nu}_\tau$ Decays and Implications for Charged Higgs Bosons,''
Phys. Rev. D \textbf{88}, no.7, 072012 (2013) doi:10.1103/PhysRevD.88.072012
{[}arXiv:1303.0571 {[}hep-ex{]}{]}.

%26

\bibitem{Belle:2015qfa} M.~Huschle \textit{et al.} {[}Belle{]},
%``Measurement of the branching ratio of $\bar{B} \to D^{(\ast)} \tau^- \bar{\nu}_\tau$ relative to $\bar{B} \to D^{(\ast)} \ell^- \bar{\nu}_\ell$ decays with hadronic tagging at Belle,''
Phys. Rev. D \textbf{92}, no.7, 072014 (2015) doi:10.1103/PhysRevD.92.072014
{[}arXiv:1507.03233 {[}hep-ex{]}{]}.

\bibitem{Belle:2019rba} G.~Caria \textit{et al.} {[}Belle{]}, %``Measurement of $\Re(D)$ and $\Re(D^*)$ with a semileptonic tagging method,''
Phys. Rev. Lett. \textbf{124}, no.16, 161803 (2020) doi:10.1103/PhysRevLett.124.161803
{[}arXiv:1910.05864 {[}hep-ex{]}{]}. %128 citations counted in INSPIRE as of 05 Dec 2022

\bibitem{Belle:leptonphoton} Recent Belle II results on semi leptonic decay anomalies $R(D)$ and $R(D^{*})$
Presented at Lepton Photon 2023, \url{https://indico.cern.ch/event/1114856/contributions/5423684/attachments/2685890/4660084/2023-07-04_LP2023_KojimaFinalVer_main.pdf}.

%30

\bibitem{LHCb:2015gmp} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Measurement of the ratio of branching fractions $\mathcal{B}(\bar{B}^0 \to D^{*+}\tau^{-}\bar{\nu}_{\tau})/\mathcal{B}(\bar{B}^0 \to D^{*+}\mu^{-}\bar{\nu}_{\mu})$,''
Phys. Rev. Lett. \textbf{115}, no.11, 111803 (2015) {[}erratum: Phys.
Rev. Lett. \textbf{115}, no.15, 159901 (2015){]} doi:10.1103/PhysRevLett.115.111803
{[}arXiv:1506.08614 {[}hep-ex{]}{]}. %1104 citations counted in INSPIRE as of 05 Dec 2022

%31

\bibitem{LHCb:2017smo} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Measurement of the ratio of the $B^0 \to D^{*-} \tau^+ \nu_{\tau}$ and $B^0 \to D^{*-} \mu^+ \nu_{\mu}$ branching fractions using three-prong $\tau$-lepton decays,''
Phys. Rev. Lett. \textbf{120}, no.17, 171802 (2018) doi:10.1103/PhysRevLett.120.171802
{[}arXiv:1708.08856 {[}hep-ex{]}{]}. %436 citations counted in INSPIRE as of 05 Dec 2022

%32

\bibitem{LHCb:2017rln} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Test of Lepton Flavor Universality by the measurement of the $B^0 \to D^{*-} \tau^+ \nu_{\tau}$ branching fraction using three-prong $\tau$ decays,''
Phys. Rev. D \textbf{97}, no.7, 072013 (2018) doi:10.1103/PhysRevD.97.072013
{[}arXiv:1711.02505 {[}hep-ex{]}{]}. %367 citations counted in INSPIRE as of 02 Dec 2022

%33

\bibitem{LHCb:2023zxo} {[}LHCb{]}, %``Measurement of the ratios of branching fractions $\Re(D^{*})$ and $\Re(D^{0})$,''
{[}arXiv:2302.02886 {[}hep-ex{]}{]}. %18 citations counted in INSPIRE as of 03 Jun 2023

\bibitem{LHCb:2023uiv}
R.~Aaij \textit{et al.} [LHCb],
%``Test of lepton flavor universality using B0\textrightarrow{}D*-\ensuremath{\tau}+\ensuremath{\nu}\ensuremath{\tau} decays with hadronic \ensuremath{\tau} channels,''
Phys. Rev. D \textbf{108}, no.1, 012018 (2023)
doi:10.1103/PhysRevD.108.012018
[arXiv:2305.01463 [hep-ex]].

%22

\bibitem{MILC:2015uhg} J.~A.~Bailey \textit{et al.} {[}MILC{]},
%``B\textrightarrow{}D\ensuremath{\ell}\ensuremath{\nu} form factors at nonzero recoil and |V$_{cb}$| from 2+1-flavor lattice QCD,''
Phys. Rev. D \textbf{92}, no.3, 034506 (2015) doi:10.1103/PhysRevD.92.034506
{[}arXiv:1503.07237 {[}hep-lat{]}{]}. %334 citations counted in INSPIRE as of 05 Dec 2022

%15

\bibitem{Na:2015kha} H.~Na \textit{et al.} {[}HPQCD{]}, %``$B \rightarrow D l \nu$ form factors at nonzero recoil and extraction of $|V_{cb}|$,''
Phys. Rev. D \textbf{92}, no.5, 054510 (2015) {[}erratum: Phys. Rev.
D \textbf{93}, no.11, 119906 (2016){]} doi:10.1103/PhysRevD.93.119906
{[}arXiv:1505.03925 {[}hep-lat{]}{]}. %341 citations counted in INSPIRE as of 05 Dec 2022

%16
\bibitem{Aoki:2016frl}
S.~Aoki, Y.~Aoki, D.~Becirevic, C.~Bernard, T.~Blum, G.~Colangelo, M.~Della Morte, P.~Dimopoulos, S.~D{\"u}rr and H.~Fukaya, \textit{et al.}
%``Review of lattice results concerning low-energy particle physics,''
Eur. Phys. J. C \textbf{77}, no.2, 112 (2017)
doi:10.1140/epjc/s10052-016-4509-7
[arXiv:1607.00299 [hep-lat]].

\bibitem{Fajfer:2012vx}
S.~Fajfer, J.~F.~Kamenik and I.~Nisandzic,
%``On the $B \to D^* \tau \bar \nu_{\tau}$ Sensitivity to New Physics,''
Phys. Rev. D \textbf{85}, 094025 (2012)
doi:10.1103/PhysRevD.85.094025
[arXiv:1203.2654 [hep-ph]].
%626 citations counted in INSPIRE as of 07 Mar 2026

\bibitem{Bigi:2016mdz}
D.~Bigi and P.~Gambino,
%``Revisiting $B\to D \ell \nu$,''
Phys. Rev. D \textbf{94}, no.9, 094008 (2016)
doi:10.1103/PhysRevD.94.094008
[arXiv:1606.08030 [hep-ph]].
%283 citations counted in INSPIRE as of 15 Aug 2023
%19

\bibitem{Bernlochner:2017jka}
F.~U.~Bernlochner, Z.~Ligeti, M.~Papucci and D.~J.~Robinson,
%``Combined analysis of semileptonic $B$ decays to $D$ and $D^*$: $R(D^{(*)})$, $|V_{cb}|$, and new physics,''
Phys. Rev. D \textbf{95}, no.11, 115008 (2017)
[erratum: Phys. Rev. D \textbf{97}, no.5, 059902 (2018)]
doi:10.1103/PhysRevD.95.115008
[arXiv:1703.05330 [hep-ph]].
%316 citations counted in INSPIRE as of 15 Aug 2023

\bibitem{Bigi:2017jbd}
D.~Bigi, P.~Gambino and S.~Schacht,
%``$R(D^*)$, $|V_{cb}|$, and the Heavy Quark Symmetry relations between form factors,''
JHEP \textbf{11}, 061 (2017)
doi:10.1007/JHEP11(2017)061
[arXiv:1707.09509 [hep-ph]].
%264 citations counted in INSPIRE as of 15 Aug 2023
%21
\bibitem{Jaiswal:2017rve}
S.~Jaiswal, S.~Nandi and S.~K.~Patra,
%``Extraction of $|V_{cb}|$ from $B\to D^{(*)}\ell\nu_\ell$ and the Standard Model predictions of $R(D^{(*)})$,''
JHEP \textbf{12}, 060 (2017)
doi:10.1007/JHEP12(2017)060
[arXiv:1707.09977 [hep-ph]].
%240 citations counted in INSPIRE as of 15 Aug 2023

\bibitem{Gambino:2019sif}
P.~Gambino, M.~Jung and S.~Schacht,
%``The $V_{cb}$ puzzle: An update,''
Phys. Lett. B \textbf{795}, 386-390 (2019)
doi:10.1016/j.physletb.2019.06.039
[arXiv:1905.08209 [hep-ph]].

\bibitem{Bordone:2019vic}
M.~Bordone, M.~Jung and D.~van Dyk,
%``Theory determination of $\bar{B}\to D^{(*)}\ell^-\bar\nu$ form factors at $\mathcal{O}(1/m_c^2)$,''
Eur. Phys. J. C \textbf{80}, no.2, 74 (2020)
doi:10.1140/epjc/s10052-020-7616-4
[arXiv:1908.09398 [hep-ph]].
%122 citations counted in INSPIRE as of 13 Sep 2023

\bibitem{Martinelli:2021onb}
G.~Martinelli, S.~Simula and L.~Vittorio,
%``$\vert V_{cb} \vert$ and $R(D)^{(*)}$) using lattice QCD and unitarity,''
Phys. Rev. D \textbf{105}, no.3, 034503 (2022)
doi:10.1103/PhysRevD.105.034503
[arXiv:2105.08674 [hep-ph]].
%50 citations counted in INSPIRE as of 13 Sep 2023

%\bibitem{HFLAV:2022pwe} Y.~Amhis \textit{et al.} {[}HFLAV{]}, ``Averages of $b$-hadron, $c$-hadron, and $\tau$-lepton properties as of 2021,''
%{[}arXiv:2206.07501 {[}hep-ex{]}{]}. %48 citations counted in INSPIRE as of 05 Dec 2022

\bibitem{HFLAV:2024link} Preliminary average of $R(D)$ and $R(D^{*})$
for Moriond 2024, \url{https://hflav-eos.web.cern.ch/hflav-eos/semi/moriond24/html/RDsDsstar/RDRDs.html}.

\bibitem{HFLAV:2025link} Preliminary average of $R(D)$ and $R(D^{*})$
for Spring 2025, \url{https://hflav-eos.web.cern.ch/hflav-eos/semi/spring25/html/RDsDsstar/RDRDs.html}.

\bibitem{LHCb:2017vlu} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Measurement of the ratio of branching fractions $\mathcal{B}(B_c^+\,\to\,J/\psi\tau^+\nu_\tau)$/$\mathcal{B}(B_c^+\,\to\,J/\psi\mu^+\nu_\mu)$,''
Phys. Rev. Lett. \textbf{120}, no.12, 121801 (2018) doi:10.1103/PhysRevLett.120.121801
{[}arXiv:1711.05623 {[}hep-ex{]}{]}. %360 citations counted in INSPIRE as of 05 Dec 2022

\bibitem{RJSi:CMS2023} CMS collaboration, "Recent CMS results on flavor anomalies and lepton flavor violation.", \url{https://indico.desy.de/event/34916/contributions/146862/}.

\bibitem{RJSi:CMS2024} CMS collaboration, "Lepton flavor (universality) violation studies at CMS.", \url{https://indico.cern.ch/event/1291157/contributions/5878345/.}.


\bibitem{LHCb:2022piu} R.~Aaij \textit{et al.} {[}LHCb{]}, %``Observation of the decay $ \Lambda_b^0\rightarrow \Lambda_c^+\tau^-\overline{\nu}_{\tau}$,''
Phys. Rev. Lett. \textbf{128}, no.19, 191803 (2022) doi:10.1103/PhysRevLett.128.191803
{[}arXiv:2201.03497 {[}hep-ex{]}{]}. %34 citations counted in INSPIRE as of 05 Dec 2022


\bibitem{Watanabe:2017mip} R.~Watanabe, %``New Physics effect on $B_c \to J/\psi %\tau\bar\nu$ in relation to the $R_{D^{(*)}}$ anomaly,''
Phys. Lett. B \textbf{776}, 5-9 (2018) doi:10.1016/j.physletb.2017.11.016
{[}arXiv:1709.08644 {[}hep-ph{]}{]}. %102 citations counted in INSPIRE as of 14 Dec 2022

\bibitem{Harrison:2020nrv}
J.~Harrison \textit{et al.} [LATTICE-HPQCD],
%``$R(J/\psi)$ and $B_c^- \rightarrow J/\psi \ell^-\bar{\nu}_\ell$ Lepton Flavor Universality Violating Observables from Lattice QCD,''
Phys. Rev. Lett. \textbf{125}, no.22, 222003 (2020)
doi:10.1103/PhysRevLett.125.222003
[arXiv:2007.06956 [hep-lat]].

\bibitem{Bernlochner:2018kxh}
F.~U.~Bernlochner, Z.~Ligeti, D.~J.~Robinson and W.~L.~Sutcliffe,
%``New predictions for $\Lambda_b\to\Lambda_c$ semileptonic decays and tests of heavy quark symmetry,''
Phys. Rev. Lett. \textbf{121}, no.20, 202001 (2018)
doi:10.1103/PhysRevLett.121.202001
[arXiv:1808.09464 [hep-ph]].

%\cite{Detmold:2015aaa}
\bibitem{Detmold:2015aaa}
W.~Detmold, C.~Lehner and S.~Meinel,
%``$\Lambda_b \to p \ell^- \bar{\nu}_\ell$ and $\Lambda_b \to \Lambda_c \ell^- \bar{\nu}_\ell$ form factors from lattice QCD with relativistic heavy quarks,''
Phys. Rev. D \textbf{92}, no.3, 034503 (2015)
doi:10.1103/PhysRevD.92.034503
[arXiv:1503.01421 [hep-lat]].
%266 citations counted in INSPIRE as of 01 Jun 2024

\bibitem{Alonso:2016oyd}
R.~Alonso, B.~Grinstein and J.~Martin Camalich,
%``Lifetime of $B_c^-$ Constrains Explanations for Anomalies in  $B\to D^{(*)}\tau\nu$,''
Phys. Rev. Lett. \textbf{118} (2017) no.8, 081802
doi:10.1103/PhysRevLett.118.081802
[arXiv:1611.06676 [hep-ph]].
%252 citations counted in INSPIRE as of 17 Aug 2023
%\cite{Gershtein:1994jw}

\bibitem{Celis:2016azn}
A.~Celis, M.~Jung, X.~Q.~Li and A.~Pich,
%``Scalar contributions to $b\to c (u) \tau \nu$ transitions,''
Phys. Lett. B \textbf{771}, 168-179 (2017)
doi:10.1016/j.physletb.2017.05.037
[arXiv:1612.07757 [hep-ph]].

%75
\bibitem{Gershtein:1994jw} S.~S.~Gershtein, V.~V.~Kiselev, A.~K.~Likhoded
and A.~V.~Tkabladze, %``Physics of B(c) mesons,''
Phys. Usp. \textbf{38}, 1-37 (1995) doi:10.1070/PU1995v038n01ABEH000063
{[}arXiv:hep-ph/9504319 {[}hep-ph{]}{]}. %181 citations counted in INSPIRE as of 31 May 2023

%76

\bibitem{Bigi:1995fs} I.~I.~Y.~Bigi, %``Inclusive B(c) decays as a QCD lab,''
Phys. Lett. B \textbf{371}, 105-110 (1996) doi:10.1016/0370-2693(95)01574-4
{[}arXiv:hep-ph/9510325 {[}hep-ph{]}{]}. %95 citations counted in INSPIRE as of 31 May 2023

%77

\bibitem{Beneke:1996xe} M.~Beneke and G.~Buchalla, %``The $B_c$ Meson Lifetime,''
Phys. Rev. D \textbf{53}, 4991-5000 (1996) doi:10.1103/PhysRevD.53.4991
{[}arXiv:hep-ph/9601249 {[}hep-ph{]}{]}. %202 citations counted in INSPIRE as of 31 May 2023

%78

\bibitem{Chang:2000ac} C.~H.~Chang, S.~L.~Chen, T.~F.~Feng
and X.~Q.~Li, %``The Lifetime of $B_c$ meson and some relevant problems,''
Phys. Rev. D \textbf{64}, 014003 (2001) doi:10.1103/PhysRevD.64.014003
{[}arXiv:hep-ph/0007162 {[}hep-ph{]}{]}. %76 citations counted in INSPIRE as of 31 May 2023

%79

\bibitem{Kiselev:2000pp} V.~V.~Kiselev, A.~E.~Kovalsky and A.~K.~Likhoded,
%``$B_c$ decays and lifetime in QCD sum rules,''
Nucl. Phys. B \textbf{585}, 353-382 (2000) doi:10.1016/S0550-3213(00)00386-2
{[}arXiv:hep-ph/0002127 {[}hep-ph{]}{]}. %195 citations counted in INSPIRE as of 31 May 2023

%80

\bibitem{Akeroyd:2017mhr} A.~G.~Akeroyd and C.~H.~Chen, %``Constraint on the branching ratio of $B_c \to \tau \bar{\nu}$ from LEP1 and consequences for $R(D^{(*)})$ anomaly,''
Phys. Rev. D \textbf{96}, no.7, 075011 (2017) doi:10.1103/PhysRevD.96.075011
{[}arXiv:1708.04072 {[}hep-ph{]}{]}. %147 citations counted in INSPIRE as of 31 May 2023

\bibitem{Belle:2016dyj} S.~Hirose \textit{et al.} {[}Belle{]}, %``Measurement of the $\tau$ lepton polarization and $R(D^*)$ in the decay $\bar{B} \to D^* \tau^- \bar{\nu}_\tau$,''
Phys. Rev. Lett. \textbf{118}, no.21, 211801 (2017) doi:10.1103/PhysRevLett.118.211801
{[}arXiv:1612.00529 {[}hep-ex{]}{]}. %599 citations counted in INSPIRE as of 05 Dec 2022



\bibitem{Belle:2017ilt} S.~Hirose \textit{et al.} {[}Belle{]}, %``Measurement of the $\tau$ lepton polarization and $R(D^*)$ in the decay $\bar{B} \rightarrow D^* \tau^- \bar{\nu}_\tau$ with one-prong hadronic $\tau$ decays at Belle,''
Phys. Rev. D \textbf{97}, no.1, 012004 (2018) doi:10.1103/PhysRevD.97.012004
{[}arXiv:1709.00129 {[}hep-ex{]}{]}. %228 citations counted in INSPIRE as of 05 Dec 2022

\bibitem{Belle:2019ewo} A.~Abdesselam \textit{et al.} {[}Belle{]},
%``Measurement of the $D^{\ast-}$ polarization in the decay $B^0 \to D^{\ast -}\tau^+\nu_{\tau}$,''
{[}arXiv:1903.03102 {[}hep-ex{]}{]}. %83 citations counted in INSPIRE as of 05 Dec 2022

%41

\bibitem{Alok:2016qyh} A.~K.~Alok, D.~Kumar, S.~Kumbhakar and
S.~U.~Sankar, %``$D^{*}$ polarization as a probe to discriminate new physics in $\bar{B}\to D^{*} \tau \bar{\nu}$,''
Phys. Rev. D \textbf{95}, no.11, 115038 (2017) doi:10.1103/PhysRevD.95.115038
{[}arXiv:1606.03164 {[}hep-ph{]}{]}. %101 citations counted in INSPIRE as of 05 Dec 2022

\bibitem{Iguro:2020cpg}
S.~Iguro and R.~Watanabe,
%``Bayesian fit analysis to full distribution data of $ \overline{\mathrm{B}}\to {\mathrm{D}}^{\left(\ast \right)}\mathrm{\ell}\overline{\nu }:\left|{\mathrm{V}}_{\mathrm{cb}}\right| $ determination and new physics constraints,''
JHEP \textbf{08}, no.08, 006 (2020)
doi:10.1007/JHEP08(2020)006
[arXiv:2004.10208 [hep-ph]].


%\cite{LHCb:2023ssl, Chen:2024zot}
\bibitem{LHCb:2023ssl}
R.~Aaij \textit{et al.} [LHCb],
%``Measurement of the D* longitudinal polarization in B0{\textrightarrow}D*-{\ensuremath{\tau}}+{\ensuremath{\nu}}{\ensuremath{\tau}} decays,''
Phys. Rev. D \textbf{110}, no.9, 092007 (2024)
doi:10.1103/PhysRevD.110.092007
[arXiv:2311.05224 [hep-ex]].

\bibitem{Chen:2024zot}
C.~Chen,
%``LHCb measurements on semileptonic decays of $b$-hadrons,''
PoS \textbf{EPS-HEP2023}, 338 (2024)
doi:10.22323/1.449.0338
%0 citations counted in INSPIRE as of 22 Sep 2024

%
\bibitem{Iguro:2024hyk}
S.~Iguro, T.~Kitahara and R.~Watanabe,
%``Global fit to b{\textrightarrow}c{\ensuremath{\tau}}{\ensuremath{\nu}} anomalies as of Spring 2024,''
Phys. Rev. D \textbf{110}, no.7, 7 (2024)
doi:10.1103/PhysRevD.110.075005
[arXiv:2405.06062 [hep-ph]].

\bibitem{Azizi:2018axf}
K.~Azizi and J.~Y.~S{\"u}ng{\"u},
%``Semileptonic $\Lambda_{b}\rightarrow \Lambda_{c}{\ell}\bar\nu_{\ell}$ Transition in Full QCD,''
Phys. Rev. D \textbf{97}, no.7, 074007 (2018)
doi:10.1103/PhysRevD.97.074007
[arXiv:1803.02085 [hep-ph]].

%\cite{Azizi:2019aaf}
\bibitem{Azizi:2019aaf}
K.~Azizi, Y.~Sarac and H.~Sundu,
%``Lepton flavor universality violation in semileptonic tree level weak transitions,''
Phys. Rev. D \textbf{99}, no.11, 113004 (2019)
doi:10.1103/PhysRevD.99.113004
[arXiv:1904.08267 [hep-ph]].

\bibitem{Asadi:2019xrc} P.~Asadi and D.~Shih, %``Maximizing the Impact of New Physics in $b\rightarrow c \tau \nu$ Anomalies,''
Phys. Rev. D \textbf{100}, no.11, 115013 (2019) doi:10.1103/PhysRevD.100.115013
{[}arXiv:1905.03311 {[}hep-ph{]}{]}. %28 citations counted in INSPIRE as of 07 Dec 2022

%51

\bibitem{Murgui:2019czp}
C.~Murgui, A.~Pe{\~n}uelas, M.~Jung and A.~Pich,
%``Global fit to $b \to c \tau \nu$ transitions,''
JHEP \textbf{09}, 103 (2019)
doi:10.1007/JHEP09(2019)103
[arXiv:1904.09311 [hep-ph]].

%52

\bibitem{Mandal:2020htr}
R.~Mandal, C.~Murgui, A.~Pe{\~n}uelas and A.~Pich,
%``The role of right-handed neutrinos in $b \to c \tau \bar{\nu}$ anomalies,''
JHEP \textbf{08}, no.08, 022 (2020)
doi:10.1007/JHEP08(2020)022
[arXiv:2004.06726 [hep-ph]].

%53

\bibitem{Cheung:2020sbq}
K.~Cheung, Z.~R.~Huang, H.~D.~Li, C.~D.~L{\"u}, Y.~N.~Mao and R.~Y.~Tang,
%``Revisit to the $b\to c\tau\nu$ transition: In and beyond the SM,''
Nucl. Phys. B \textbf{965}, 115354 (2021)
doi:10.1016/j.nuclphysb.2021.115354
[arXiv:2002.07272 [hep-ph]].
%55 citations counted in INSPIRE as of 07 Mar 2026

%\cite{Colangelo:2020vhu}
\bibitem{Colangelo:2020vhu}
P.~Colangelo, F.~De Fazio and F.~Loparco,
%``Inclusive semileptonic $\Lambda_{b}$ decays in the Standard Model and beyond,''
JHEP \textbf{11}, 032 (2020)
[erratum: JHEP \textbf{12}, 098 (2022)]
doi:10.1007/JHEP11(2020)032
[arXiv:2006.13759 [hep-ph]].

%54

\bibitem{Sahoo:2019hbu} S.~Sahoo and R.~Mohanta, %``Investigating the role of new physics in $b \to c \tau \bar \nu_\tau$ transitions,''
{[}arXiv:1910.09269 {[}hep-ph{]}{]}. %14 citations counted in INSPIRE as of 07 Dec 2022

%55

\bibitem{Shi:2019gxi}
R.~X.~Shi, L.~S.~Geng, B.~Grinstein, S.~J{\"a}ger and J.~Martin Camalich,
%``Revisiting the new-physics interpretation of the $b\to c\tau\nu$ data,''
JHEP \textbf{12}, 065 (2019)
doi:10.1007/JHEP12(2019)065
[arXiv:1905.08498 [hep-ph]].

%56

\bibitem{Bardhan:2019ljo} D.~Bardhan and D.~Ghosh, %``$B$ -meson charged current anomalies: The post-Moriond 2019 status,''
Phys. Rev. D \textbf{100}, no.1, 011701 (2019) doi:10.1103/PhysRevD.100.011701
{[}arXiv:1904.10432 {[}hep-ph{]}{]}. %44 citations counted in INSPIRE as of 07 Dec 2022

%57

\bibitem{Blanke:2018yud}
M.~Blanke, A.~Crivellin, S.~de Boer, T.~Kitahara, M.~Moscati, U.~Nierste and I.~Ni{\v{s}}and{\v{z}}i{\'c},
%``Impact of polarization observables and $ B_c\to \tau \nu$ on new physics explanations of the $b\to c \tau \nu$ anomaly,''
Phys. Rev. D \textbf{99}, no.7, 075006 (2019)
doi:10.1103/PhysRevD.99.075006
[arXiv:1811.09603 [hep-ph]].

%58

\bibitem{Fedele:2022iib}
M.~Fedele, M.~Blanke, A.~Crivellin, S.~Iguro, T.~Kitahara, U.~Nierste and R.~Watanabe,
%``Impact of {\ensuremath{\Lambda}}b{\textrightarrow}{\ensuremath{\Lambda}}c{\ensuremath{\tau}}{\ensuremath{\nu}} measurement on new physics in b{\textrightarrow}cl{\ensuremath{\nu}} transitions,''
Phys. Rev. D \textbf{107}, no.5, 055005 (2023)
doi:10.1103/PhysRevD.107.055005
[arXiv:2211.14172 [hep-ph]].

\bibitem{Blanke:2019qrx} M.~Blanke, A.~Crivellin, T.~Kitahara, M.~Moscati, U.~Nierste and I.~Ni\v{s}and\v{z}i\'c,
%``Addendum to \textquotedblleft{}Impact of polarization observables and $B_c\to \tau \nu$ on new physics explanations of the $b\to c \tau \nu$ anomaly'',''
doi:10.1103/PhysRevD.100.035035
[arXiv:1905.08253 [hep-ph]].

%60

\bibitem{Alok:2019uqc} A.~K.~Alok, D.~Kumar, S.~Kumbhakar and
S.~Uma Sankar, %``Solutions to $R_D$-$R_{D^*}$ in light of Belle 2019 data,''
Nucl. Phys. B \textbf{953}, 114957 (2020) doi:10.1016/j.nuclphysb.2020.114957
{[}arXiv:1903.10486 {[}hep-ph{]}{]}. %42 citations counted in INSPIRE as of 07 Dec 2022

%61

\bibitem{Huang:2018nnq} Z.~R.~Huang, Y.~Li, C.~D.~Lu, M.~A.~Paracha
and C.~Wang, %``Footprints of New Physics in $b\to c\tau\nu$ Transitions,''
Phys. Rev. D \textbf{98}, no.9, 095018 (2018) doi:10.1103/PhysRevD.98.095018
{[}arXiv:1808.03565 {[}hep-ph{]}{]}. %91 citations counted in INSPIRE as of 07 Dec 2022

%62
%\cite{Arslan:2023wgk, Yasmeen:2024cki}
\bibitem{Arslan:2023wgk}
M.~Arslan, T.~Yasmeen, S.~Shafaq, I.~Ahmed and M.~J.~Aslam,
%``Analysis of anomalies using weak effective Hamiltonian with complex couplings and their impact on various physical observables,''
Chin. Phys. C \textbf{48}, no.8, 083103 (2024)
doi:10.1088/1674-1137/ad34bc
[arXiv:2309.09929 [hep-ph]].
%1 citations counted in INSPIRE as of 22 Sep 2024

%\cite{Yasmeen:2024cki}
\bibitem{Yasmeen:2024cki}
T.~Yasmeen, I.~Ahmed, S.~Shafaq, M.~Arslan and M.~J.~Aslam,
%``Probing New Physics in Light of Recent Developments in b \textrightarrow{} c \ensuremath{\ell} v Transitions,''
PTEP \textbf{2024}, no.7, 073B07 (2024)
doi:10.1093/ptep/ptae086
[arXiv:2401.02334 [hep-ph]].
%1 citations counted in INSPIRE as of 22 Sep 2024

%\cite{Huang:2025kof}
\bibitem{Huang:2025kof}
Z.~R.~Huang, F.~M.~Bhutta, N.~Farooq, M.~A.~Paracha and Y.~Li,
%``Reinvestigating the semileptonic B{\textrightarrow}D(*){\ensuremath{\tau}}{\ensuremath{\nu}}{\textasciimacron}{\ensuremath{\tau}} decays in the model independent scenarios and leptoquark models,''
Phys. Rev. D \textbf{111}, no.11, 115035 (2025)
doi:10.1103/PhysRevD.111.115035
[arXiv:2501.03734 [hep-ph]].
%3 citations counted in INSPIRE as of 08 Mar 2026

%\cite{Tang:2022nqm}
\bibitem{Tang:2022nqm}
R.~Y.~Tang, Z.~R.~Huang, C.~D.~L{\"u} and R.~Zhu,
%``Scrutinizing new physics in semi-leptonic B $_{c}$ {\textrightarrow} J/{\ensuremath{\psi}}{\ensuremath{\tau}}{\ensuremath{\nu}} decay,''
J. Phys. G \textbf{49}, no.11, 115003 (2022)
doi:10.1088/1361-6471/ac8d1e
[arXiv:2204.04357 [hep-ph]].
%15 citations counted in INSPIRE as of 08 Mar 2026

\bibitem{Greljo:2018ogz} A.~Greljo, D.~J.~Robinson, B.~Shakya
and J.~Zupan, %``R(D$^{(?)}$) from W$^{?}$ and right-handed neutrinos,''
JHEP \textbf{09}, 169 (2018) doi:10.1007/JHEP09(2018)169 {[}arXiv:1804.04642
{[}hep-ph{]}{]}. %90 citations counted in INSPIRE as of 14 Dec 2022

%63

\bibitem{Azatov:2018kzb} A.~Azatov, D.~Barducci, D.~Ghosh, D.~Marzocca
and L.~Ubaldi, %``Combined explanations of B-physics anomalies: the sterile neutrino solution,''
JHEP \textbf{10}, 092 (2018) doi:10.1007/JHEP10(2018)092 {[}arXiv:1807.10745
{[}hep-ph{]}{]}. %73 citations counted in INSPIRE as of 14 Dec 2022

%64

\bibitem{Heeck:2018ntp} J.~Heeck and D.~Teresi, %``Pati-Salam explanations of the B-meson anomalies,''
JHEP \textbf{12}, 103 (2018) doi:10.1007/JHEP12(2018)103 {[}arXiv:1808.07492
{[}hep-ph{]}{]}. %77 citations counted in INSPIRE as of 14 Dec 2022

%65

\bibitem{Babu:2018vrl} K.~S.~Babu, B.~Dutta and R.~N.~Mohapatra,
%``A theory of R(D$^{*}$, D) anomaly with right-handed currents,''
JHEP \textbf{01}, 168 (2019) doi:10.1007/JHEP01(2019)168 {[}arXiv:1811.04496
{[}hep-ph{]}{]}. %43 citations counted in INSPIRE as of 14 Dec 2022

%66

\bibitem{He:2017bft} X.~G.~He and G.~Valencia, %``Lepton universality violation and right-handed currents in $b \to c \tau \nu$,''
Phys. Lett. B \textbf{779}, 52-57 (2018) doi:10.1016/j.physletb.2018.01.073
{[}arXiv:1711.09525 {[}hep-ph{]}{]}. %47 citations counted in INSPIRE as of 14 Dec 2022

%67

\bibitem{Gomez:2019xfw}
J.~D.~G{\'o}mez, N.~Quintero and E.~Rojas,
%``Charged current $b \to c \tau \bar{\nu}_\tau$ anomalies in a general $W^\prime$ boson scenario,''
Phys. Rev. D \textbf{100}, no.9, 093003 (2019)
doi:10.1103/PhysRevD.100.093003
[arXiv:1907.08357 [hep-ph]].

%68

\bibitem{Alguero:2020ukk}
M.~Alguer{\'o}, S.~Descotes-Genon, J.~Matias and M.~Novoa-Brunet,
%``Symmetries in $B \to D^* \ell \nu$ angular observables,''
JHEP \textbf{06}, 156 (2020)
doi:10.1007/JHEP06(2020)156
[arXiv:2003.02533 [hep-ph]].
%69

\bibitem{Dutta:2013qaa} R.~Dutta, A.~Bhol and A.~K.~Giri, %``Effective theory approach to new physics in b \textrightarrow{} u and b \textrightarrow{} c leptonic and semileptonic decays,''
Phys. Rev. D \textbf{88}, no.11, 114023 (2013) doi:10.1103/PhysRevD.88.114023
{[}arXiv:1307.6653 {[}hep-ph{]}{]}. %61 citations counted in INSPIRE as of 14 Dec 2022

%70

\bibitem{Dutta:2017xmj} R.~Dutta and A.~Bhol, %``$B_c \to (J/\psi,\,\eta_c)\tau\nu$ semileptonic decays within the standard model and beyond,''
Phys. Rev. D \textbf{96}, no.7, 076001 (2017) doi:10.1103/PhysRevD.96.076001
{[}arXiv:1701.08598 {[}hep-ph{]}{]}. %83 citations counted in INSPIRE as of 14 Dec 2022

%71

\bibitem{Dutta:2017wpq} R.~Dutta, %``Exploring $R_D$, $R_{D^{\ast}}$ and $R_{J/\Psi}$ anomalies,''
{[}arXiv:1710.00351 {[}hep-ph{]}{]}. %37 citations counted in INSPIRE as of 14 Dec 2022

%72

\bibitem{Dutta:2018jxz} R.~Dutta and N.~Rajeev, %``Signature of lepton flavor universality violation in $B_s \to D_s\tau\nu$  semileptonic decays,''
Phys. Rev. D \textbf{97}, no.9, 095045 (2018) doi:10.1103/PhysRevD.97.095045
{[}arXiv:1803.03038 {[}hep-ph{]}{]}. %18 citations counted in INSPIRE as of 14 Dec 2022

\bibitem{Freytsis:2015qca}
M.~Freytsis, Z.~Ligeti and J.~T.~Ruderman,
%``Flavor models for $\bar{B} \to D^{(*)} \tau \bar{\nu}$,''
Phys. Rev. D \textbf{92}, no.5, 054018 (2015)
doi:10.1103/PhysRevD.92.054018
[arXiv:1506.08896 [hep-ph]].
%344 citations counted in INSPIRE as of 08 Jul 2024

%\cite{Alok:2017qsi}
\bibitem{Alok:2017qsi}
A.~K.~Alok, D.~Kumar, J.~Kumar, S.~Kumbhakar and S.~U.~Sankar,
%``New physics solutions for $R_D$ and $R_{D^*}$,''
JHEP \textbf{09}, 152 (2018)
doi:10.1007/JHEP09(2018)152
[arXiv:1710.04127 [hep-ph]].
%85 citations counted in INSPIRE as of 04 Jun 2024
%\cite{Arslan:2025zph}
\bibitem{Arslan:2025zph}
M.~Arslan, I.~Ahmed, M.~J.~Aslam, S.~Shafaq and T.~Yasmeen,
Int. J. Mod. Phys. A \textbf{40}, no.30, 2550151 (2025)
doi:10.1142/S0217751X25501519
[arXiv:2510.11564 [hep-ph]].
%0 citations counted in INSPIRE as of 16 Oct 2025

\bibitem{Gutsche:2015rrt}
T.~Gutsche, M.~A.~Ivanov, J.~G.~Korner, V.~E.~Lyubovitskij and P.~Santorelli,
%``Semileptonic decays $\Lambda_c^+ \to \Lambda \ell^+ \nu_\ell\,\,(\ell=e,\mu)$ in the covariant quark model and comparison with the new absolute branching fraction measurements of Belle and BESIII,''
Phys. Rev. D \textbf{93}, no.3, 034008 (2016)
doi:10.1103/PhysRevD.93.034008
[arXiv:1512.02168 [hep-ph]].

\bibitem{Gutsche:2015mxa}
T.~Gutsche, M.~A.~Ivanov, J.~G.~K\"orner, V.~E.~Lyubovitskij, P.~Santorelli and N.~Habyl,
%``Semileptonic decay $\Lambda_b \to \Lambda_c + \tau^- + \bar{\nu_\tau}$ in the covariant confined quark model,''
Phys. Rev. D \textbf{91}, no.7, 074001 (2015)
[erratum: Phys. Rev. D \textbf{91}, no.11, 119907 (2015)]
doi:10.1103/PhysRevD.91.074001
[arXiv:1502.04864 [hep-ph]].

\bibitem{Shivashankara:2015cta}
S.~Shivashankara, W.~Wu and A.~Datta,
%``$\Lambda_b \to \Lambda_c \tau \bar{\nu}_{\tau}$ Decay in the Standard Model and with New Physics,''
Phys. Rev. D \textbf{91}, no.11, 115003 (2015)
doi:10.1103/PhysRevD.91.115003
[arXiv:1502.07230 [hep-ph]].

\bibitem{Dutta:2015ueb}
R.~Dutta,
%``$\Lambda_b \to (\Lambda_c,\,p)\,\tau\,\nu$ decays within standard model and beyond,''
Phys. Rev. D \textbf{93}, no.5, 054003 (2016)
doi:10.1103/PhysRevD.93.054003
[arXiv:1512.04034 [hep-ph]].

\bibitem{Faustov:2016pal}
R.~N.~Faustov and V.~O.~Galkin,
%``Semileptonic decays of $\Lambda_b$ baryons in the relativistic quark model,''
Phys. Rev. D \textbf{94}, no.7, 073008 (2016)
doi:10.1103/PhysRevD.94.073008
[arXiv:1609.00199 [hep-ph]].

\bibitem{Li:2016pdv}
X.~Q.~Li, Y.~D.~Yang and X.~Zhang,
%``$ {\varLambda}_b\to {\varLambda}_c\tau {\overline{\nu}}_{\tau } $ decay in scalar and vector leptoquark scenarios,''
JHEP \textbf{02}, 068 (2017)
doi:10.1007/JHEP02(2017)068
[arXiv:1611.01635 [hep-ph]].

%81
%\cite{Datta:2017aue}
\bibitem{Datta:2017aue}
A.~Datta, S.~Kamali, S.~Meinel and A.~Rashed,
%``Phenomenology of $ {\Lambda}_b\to {\Lambda}_c\tau {\overline{\nu}}_{\tau } $ using lattice QCD calculations,''
JHEP \textbf{08}, 131 (2017)
doi:10.1007/JHEP08(2017)131
[arXiv:1702.02243 [hep-ph]].
%97 citations counted in INSPIRE as of 01 Jun 2024
%\cite{Bhattacharya:2020lfm}

\bibitem{Bhattacharya:2020lfm}
B.~Bhattacharya, A.~Datta, S.~Kamali and D.~London,
%``A measurable angular distribution for $ \overline{B}\to {D}^{\ast }{\tau}^{-}{\overline{v}}_{\tau } $ decays,''
JHEP \textbf{07}, no.07, 194 (2020)
doi:10.1007/JHEP07(2020)194
[arXiv:2005.03032 [hep-ph]].
%37 citations counted in INSPIRE as of 25 Oct 2025
%\cite{Hu:2020axt}

\bibitem{Hu:2020axt}
Q.~Y.~Hu, X.~Q.~Li, Y.~D.~Yang and D.~H.~Zheng,
%``The measurable angular distribution of $ {\Lambda}_b^0\to {\Lambda}_c^{+}\left(\to {\Lambda}^0{\pi}^{+}\right){\tau}^{-}\left(\to {\pi}^{-}{v}_{\tau}\right){\overline{v}}_{\tau } $ decay,''
JHEP \textbf{02}, 183 (2021)
doi:10.1007/JHEP02(2021)183
[arXiv:2011.05912 [hep-ph]].


\bibitem{Buchmuller:1985jz}
W.~Buchmuller and D.~Wyler,
%``Effective Lagrangian Analysis of New Interactions and Flavor Conservation,''
Nucl. Phys. B \textbf{268}, 621-653 (1986)
doi:10.1016/0550-3213(86)90262-2

\bibitem{Grzadkowski:2010es}
B.~Grzadkowski, M.~Iskrzynski, M.~Misiak and J.~Rosiek,
%``Dimension-Six Terms in the Standard Model Lagrangian,''
JHEP \textbf{10}, 085 (2010)
doi:10.1007/JHEP10(2010)085
[arXiv:1008.4884 [hep-ph]].

\bibitem{Aebischer:2015fzz}
J.~Aebischer, A.~Crivellin, M.~Fael and C.~Greub,
%``Matching of gauge invariant dimension-six operators for $b\to s$ and $b\to c$ transitions,''
JHEP \textbf{05}, 037 (2016)
doi:10.1007/JHEP05(2016)037
[arXiv:1512.02830 [hep-ph]].

\bibitem{Gonzalez-Alonso:2017iyc}
M.~Gonz{\'a}lez-Alonso, J.~Martin Camalich and K.~Mimouni,
%``Renormalization-group evolution of new physics contributions to (semi)leptonic meson decays,''
Phys. Lett. B \textbf{772}, 777-785 (2017)
doi:10.1016/j.physletb.2017.07.003
[arXiv:1706.00410 [hep-ph]].
%127 citations counted in INSPIRE as of 06 Sep 2023
\bibitem{Iguro:2018vqb} S.~Iguro, T.~Kitahara, Y.~Omura, R.~Watanabe
and K.~Yamamoto, %``D$^{*}$ polarization vs. $ {R}_{D^{\left(\ast \right)}} $ anomalies in the leptoquark models,''
JHEP \textbf{02}, 194 (2019) doi:10.1007/JHEP02(2019)194 {[}arXiv:1811.08899
{[}hep-ph{]}{]}. %76 citations counted in INSPIRE as of 14 Dec 2022

%82

\bibitem{Asadi:2018wea} P.~Asadi, M.~R.~Buckley and D.~Shih,
%``It\textquoteright{}s all right(-handed neutrinos): a new W$^{?}$ model for the $ {R}_{D^{{\left(\ast \right)}}} $ anomaly,''
JHEP \textbf{09}, 010 (2018) doi:10.1007/JHEP09(2018)010 {[}arXiv:1804.04135
{[}hep-ph{]}{]}. %80 citations counted in INSPIRE as of 14 Dec 2022

%83

\bibitem{Asadi:2018sym} P.~Asadi, M.~R.~Buckley and D.~Shih,
%``Asymmetry Observables and the Origin of $R_{D^{(*)}}$ Anomalies,''
Phys. Rev. D \textbf{99}, no.3, 035015 (2019) doi:10.1103/PhysRevD.99.035015
{[}arXiv:1810.06597 {[}hep-ph{]}{]}. %35 citations counted in INSPIRE as of 14 Dec 2022

%84

\bibitem{Ligeti:2016npd} Z.~Ligeti, M.~Papucci and D.~J.~Robinson,
%``New Physics in the Visible Final States of $B\to D^{(*)}\tau\nu$,''
JHEP \textbf{01}, 083 (2017) doi:10.1007/JHEP01(2017)083 {[}arXiv:1610.02045
{[}hep-ph{]}{]}. %73 citations counted in INSPIRE as of 14 Dec 2022

%85

\bibitem{Robinson:2018gza} D.~J.~Robinson, B.~Shakya and J.~Zupan,
%``Right-handed neutrinos and R(D$^{(?)}$),''
JHEP \textbf{02}, 119 (2019) doi:10.1007/JHEP02(2019)119 {[}arXiv:1807.04753
{[}hep-ph{]}{]}. %59 citations counted in INSPIRE as of 14 Dec 2022

%\cite{Becirevic:2019tpx}

\bibitem{Cardozo:2020uol}
J.~Cardozo, J.~H.~Mu{\~n}oz, N.~Quintero and E.~Rojas,
%``Analysing the charged scalar boson contribution to the charged-current $B$ meson anomalies,''
J. Phys. G \textbf{48}, no.3, 035001 (2021)
doi:10.1088/1361-6471/abc865
[arXiv:2006.07751 [hep-ph]].
%14 citations counted in INSPIRE as of 04 Sep 2023
%87

\bibitem{Kamali:2018bdp} S.~Kamali, %``New physics in inclusive semileptonic $B$ decays including nonperturbative corrections,''
Int. J. Mod. Phys. A \textbf{34}, no.06n07, 1950036 (2019) doi:10.1142/S0217751X19500362
{[}arXiv:1811.07393 {[}hep-ph{]}{]}. %12 citations counted in INSPIRE as of 05 Dec 2022

\bibitem{Iguro:2022yzr}
S.~Iguro, T.~Kitahara and R.~Watanabe,
%``Global fit to $b \to c\tau\nu$ anomalies 2022 mid-autumn,''
[arXiv:2210.10751 [hep-ph]]


\bibitem{Greljo:2018tzh}
A.~Greljo, J.~Martin Camalich and J.~D.~Ruiz-\'Alvarez,
%``Mono-$\tau$ Signatures at the LHC Constrain Explanations of $B$-decay Anomalies,''
Phys. Rev. Lett. \textbf{122}, no.13, 131803 (2019)
doi:10.1103/PhysRevLett.122.131803
[arXiv:1811.07920 [hep-ph]].

\bibitem{Faroughy:2016osc}
D.~A.~Faroughy, A.~Greljo and J.~F.~Kamenik,
%``Confronting lepton flavor universality violation in B decays with high-$p_T$ tau lepton searches at LHC,''
Phys. Lett. B \textbf{764}, 126-134 (2017)
doi:10.1016/j.physletb.2016.11.011
[arXiv:1609.07138 [hep-ph]].

\bibitem{Iguro:2018fni}
S.~Iguro, Y.~Omura and M.~Takeuchi,
%``Test of the $R(D^{(*)})$ anomaly at the LHC,''
Phys. Rev. D \textbf{99}, no.7, 075013 (2019)
doi:10.1103/PhysRevD.99.075013
[arXiv:1810.05843 [hep-ph]].

\bibitem{Endo:2021lhi}
M.~Endo, S.~Iguro, T.~Kitahara, M.~Takeuchi and R.~Watanabe,
%``Non-resonant new physics search at the LHC for the b \textrightarrow{} c\ensuremath{\tau}\ensuremath{\nu} anomalies,''
JHEP \textbf{02}, 106 (2022)
doi:10.1007/JHEP02(2022)106
[arXiv:2111.04748 [hep-ph]].

\bibitem{ParticleDataGroup:2024cfk}
S.~Navas \textit{et al.} [Particle Data Group],
%``Review of particle physics,''
Phys. Rev. D \textbf{110}, no.3, 030001 (2024)
doi:10.1103/PhysRevD.110.030001
%3938 citations counted in INSPIRE as of 31 Jan 2026

\end{thebibliography}

\end{document}
