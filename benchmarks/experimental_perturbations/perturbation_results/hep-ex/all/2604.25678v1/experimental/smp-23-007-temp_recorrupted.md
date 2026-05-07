\documentclass[11pt,twoside,a4paper,cmspaper,final,collab]{cms-tdr}
\def\svnVersion{4025bad-D}\def\svnDate{2026/04/28}\def\cmsCernNoTag{CERN-EP-2026-099}\def\cmsCernDate{\today}\def\cmsMessage{Submitted to Physics Letters B}
\begin{document}\cmsNoteHeader{SMP-23-007}


\providecommand{\cmsTable}[1]{\resizebox{\textwidth}{!}{#1}}
\ifthenelse{\boolean{cms@external}}{\providecommand{\cmsLeft}{upper\xspace}}{\providecommand{\cmsLeft}{left\xspace}}
\ifthenelse{\boolean{cms@external}}{\providecommand{\cmsRight}{lower\xspace}}{\providecommand{\cmsRight}{right\xspace}}


\providecommand{\PGgst}{\HepParticle{\PGg}{}{\star}\xspace}
\newcommand{\PGZ}{\ensuremath{\PGgst/\PZ}\xspace}
\newcommand{\ptll}{\ensuremath{\pt^{\Pell\Pell}}\xspace}
\newcommand{\yll}{\ensuremath{y^{\Pell\Pell}}\xspace}
\newcommand{\mll}{\ensuremath{m_{\Pell\Pell}}\xspace}
\newcommand{\ptmm}{\ensuremath{\pt^{\PGm\PGm}}\xspace}
\newcommand{\ymm}{\ensuremath{y^{\PGm\PGm}}\xspace}
\newcommand{\mmm}{\ensuremath{m_{\PGm\PGm}}\xspace}
\newcommand{\ptm}{\ensuremath{\pt^{\PGm}}\xspace}

\cmsNoteHeader{SMP-23-007}

\title{Measurement of the \texorpdfstring{$\PZ \to \PGmp\PGmm$}{Z to mu+mu-} angular coefficients in \texorpdfstring{$\Pp\Pp$}{pp} collisions at \texorpdfstring{$\sqrt{s} = 13\TeV$}{sqrt(s) = 13 TeV} as functions of transverse momentum and rapidity}


\author[cern]{the CMS Collaboration}

\date{\today}

\abstract{A measurement of the eight angular polarization coefficients, $A_0$ to $A_7$, in the cross section for the Drell--Yan production of two muons is presented. The analysis is based on proton-proton ($\Pp\Pp$) collision data recorded with the CMS detector at the LHC at a center-of-mass energy of $\sqrt{s}=13\TeV$, corresponding to an integrated luminosity of 140\fbinv. The coefficients are determined double differentially in eight intervals of transverse momentum and two intervals of rapidity of the muon pair $\PGmp\PGmm$. The results are presented for the $\PGmp\PGmm$ invariant mass range 81--101\GeV and are compared with theoretical predictions calculated at next-to-next-to-leading order in perturbative quantum chromodynamics. The measurement provides relevant information about the underlying partonic dynamics and the \PZ boson production mechanisms.}

\hypersetup{%
pdfauthor={CMS Collaboration},%
pdftitle={Measurement of the Z to mu+mu- angular coefficients in pp collisions at sqrt(s) = 13 TeV as functions of transverse momentum and rapidity},%
pdfsubject={CMS},%
pdfkeywords={CMS, electroweak, Z polarization, angular coefficients}}

\maketitle 

\section{Introduction}

Processes with dilepton final states play a key role in collider experiments, providing clean experimental signatures and precise probes of the underlying dynamics of particle interactions. Particularly, the Drell--Yan (DY) process ($\Pp\Pp \to \PGZ \to \ell^+\ell^-$, where $\Pp\Pp$ stands for proton-proton collisions and $\ell$ represents the $\Pe$, $\PGm$, and $\PGt$ leptons)~\cite{Drell-Yan_1970} is sensitive to the electroweak (EW) \PGZ couplings and also provides unique information about lepton-hadron correlations~\cite{Mirkes_WandZPolarizEffects_1994, Mirkes_AngDecayDistrW-bosNLO_1992}. Such correlations are essential for understanding the dynamics of the initial-state partons and the effects of quantum chromodynamics (QCD), offering a window into parton distribution functions (PDFs)~\cite{Bodek_UsingAfbForPDF_2015, Zhang_EtractBoerMulder_2008, TMDandAC_2024} and their connection with the angular structure of the final states. Within the parton model, this connection is encoded in eight angular polarization coefficients $A_i$ ($i=0,\ldots,7$). 

We consider the DY process in the Collins--Soper (CS) frame~\cite{CollinsSoper_1977}, where the $z$ axis bisects the angle between the momentum vectors of the colliding protons, with the positive direction pointing closer to the momentum direction of the lepton pair, \ie of the \PGZ boson in the laboratory frame. The $x$ axis lies in the same plane as the momenta of the colliding protons, but orthogonal to the $z$ axis. The $y$ axis is then defined to complete the right-handed system. To be consistent with previous measurements~\cite{CMS_AiMeasur_8TeV_2015, ATLAS_AiMeasur_8TeV_2016}, the momentum of the beam proton closest in rapidity to the \PGZ boson is considered the ``target momentum" in our measurement.

The differential cross section depends on the azimuthal angle $\phi^*$ and polar angle $\theta^*$ as
\ifthenelse{\boolean{cms@external}}
{ % Begin journal version
\begin{multline}
\frac{\rd^2\sigma}{\rd\theta^*\rd\phi^*} \propto 
(1+\cos^2 \theta^*) 
+ A_0\frac{1}{2}(1-3\,\cos^2 \theta^*) \\
+ A_1\sin(2\theta^*)\cos\phi^* 
+ A_2\frac{1}{2}\sin^2 \theta^*\cos(2\phi^*) \\
+ A_3\sin \theta^*\cos \phi^* 
+ A_4\cos \theta^* 
+ A_5\sin^2 \theta^*\sin(2\phi^*) \\
+ A_6\sin(2\theta^*)\sin\phi^* 
+ A_7\sin\phi^*\sin\theta^*.
\label{DoubleDiffCrossSection}
\end{multline}
}
{ % Begin arXiv version
\begin{multline}
\frac{\rd^2\sigma}{\rd\theta^*\rd\phi^*} \propto (1+\cos^2 \theta^*)+A_0\frac{1}{2}(1-3\,\cos^2 \theta^*)+A_1\sin(2\theta^*)\cos\phi^*+A_2\frac{1}{2}\sin^2 \theta^*\cos(2\phi^*)\\
+A_3\sin \theta^*\cos \phi^*+A_4\cos \theta^*+A_5\sin^2 \theta^*\sin(2\phi^*)+A_6\sin(2\theta^*)\sin\phi^*+A_7\sin\phi^*\sin\theta^*.
\label{DoubleDiffCrossSection}
\end{multline}
}
Figure~\ref{fig_CollinsSoperFrame} illustrates the definition of the $\phi^*$ and $\theta^*$ angles 
in the CS frame.  

\begin{figure}[ht]
\centering
\includegraphics[width=0.48\textwidth]{Figure_001.pdf}
\caption{The definition of the CS frame and angles $\phi^*$ and $\theta^*$ of the negatively charged lepton produced in the \PGZ decay. The $p_1$ and $p_2$ vectors indicate the directions of the incoming proton's momenta in the dilepton rest frame and $\ell$ indicates the momentum of the negatively charged lepton~\cite{FigOfCollinsSoper_2017}.}
\label{fig_CollinsSoperFrame}
\end{figure} 

The angular polarization coefficients $A_i$ are functions of the lepton pair kinematic variables: transverse momentum \ptll, rapidity \yll, and invariant mass \mll. They define modulations in the angular distribution of the leptons, reflecting contributions of different polarization states of the \PGZ boson. Importantly, these coefficients correspond to orthogonal angular terms in Eq.~(\ref{DoubleDiffCrossSection}). The coefficients reflect processes occurring at the parton level. In calculations at leading order (LO) in QCD, all are expected to be close to zero at $\ptll \approx 0$, except for $A_4$, which describes the magnitude of asymmetry of the $\cos \theta^*$ distribution around zero. This phenomenon is also known as the forward-backward asymmetry $(A_{\text{FB}})$ and is a consequence of the parity violating nature of the EW decay of the \PGZ boson to a lepton pair. The coefficients $A_0$ and $A_2$ parametrize the longitudinal (L) polarization fraction of the \PGZ boson and the interference between its transverse (T) polarization states, respectively. The Lam--Tung relation $A_0 - A_2 = 0$~\cite{LumTung_1978} holds at leading order in perturbative QCD as a consequence of helicity conservation and the vector nature of the mediating boson. Deviations from this relation can occur because of higher-order QCD radiation, noncollinear parton dynamics, and other effects resulting from the intrinsic transverse momentum of the interacting partons~\cite{Faccioli_RotationInvariant_2010, Faccioli_ParticlePolarization_Book_2022, PENG_Teryaev_2016, Boer_IntrinsicTranverseMomentum1999}. The coefficient $A_1$ encodes the interference between longitudinal and transverse polarization states. The $A_3$ and $A_4$ coefficients are based on the axial and vector EW couplings of quarks and leptons. The coefficient $A_4$ is used for precise measurements of the squared sine of the effective EW mixing angle $\sin^2\theta_W^{\text{eff}}$~\cite{CDF_InderectSinThetaMeasur_1.96TeV_2013, CDF_FirstAiMeasur_1.96TeV_2011, WeakMixAngle_Meas_CMS_2025}. The $A_5$, $A_6$, and $A_7$ coefficients define the contribution of T-odd asymmetries to the total cross section and may be non-zero in one-loop processes at next-to-next-to-leading order (NNLO) in QCD~\cite{HAGIWARA_ToddAsym_1983, HAGIWARA_ProbOneLoop_1992}.

Some of the coefficients ($A_0$, $A_2$, $A_3$, and $A_4$) were measured for the first time in $\Pp\PAp$ collisions at a center-of-mass energy of 1.96\TeV at the Fermilab Tevatron by the CDF Collaboration~\cite{CDF_FirstAiMeasur_1.96TeV_2011}. More recent $A_i$ measurements were performed by the CMS~\cite{CMS_AiMeasur_8TeV_2015} and ATLAS~\cite{ATLAS_AiMeasur_8TeV_2016} Collaborations based on the LHC Run 1 data. The amount of data collected at $\sqrt{s} = 8$\TeV allowed measuring $A_0,A_1,A_2,A_3$, and $A_4$ in the \PZ pole region as functions of \PZ boson rapidity and transverse momentum, and made it possible to unequivocally establish a violation of the Lam--Tung relation. Moreover, ATLAS performed measurements using the combined $\EE$ and $\MM$ sample that indicated evidence of non-zero $A_5$, $A_6$, and $A_7$ with a significance of three standard deviations. In 2022, the LHCb Collaboration published the first measurement of the coefficients $A_0$ to $A_4$ in the dimuon channel in the forward rapidity region ($\ymm>2$) with dimuon transverse momentum $\ptmm<100$\GeV~\cite{LHCb_AiMeas_13TeV_2022}. To date, all the measurements agree with theoretical calculations at NNLO precision in QCD.

This Letter presents a measurement of the full set of angular polarization coefficients $A_0$ to $A_7$ in the DY dimuon channel process $(\Pp\Pp \to \PZ \to \MM)$ using LHC $\Pp\Pp$ collision data collected by the CMS experiment at $\sqrt{s} = 13$\TeV in 2016--2018. The data sample corresponds to an integrated luminosity of 140\fbinv. The results are compared with NNLO QCD predictions as a function of the dimuon rapidity and transverse momentum for $\abs{\ymm}<2.4$ and $\ptmm<400$\GeV.
The numerical values are reported in the HEPData record of this analysis~\cite{HEPData}.

\section{The CMS detector and event selection}

The CMS apparatus~\cite{CMS:2008xjf} is a multipurpose, nearly hermetic detector, designed to trigger on~\cite{CMS:2020cmk,CMS:2016ngn} and identify electrons, muons, photons, and charged hadrons~\cite{CMS:2020uim,CMS:2018rym,CMS:2014pgm}. A global particle-flow (PF) algorithm~\cite{CMS:2017yfk} reconstructs all individual particle candidates in an event, combining information provided by the all-silicon tracker and by the crystal electromagnetic, and a brass and scintillator hadron calorimeters, operating inside a 3.8\unit{T} superconducting solenoid, with data from the gas-ionization muon detectors embedded in the flux-return yoke outside the solenoid. Muons are measured in the pseudorapidity range $\abs{\eta} < 2.4$, with detection planes made using three technologies: drift tubes, cathode strip chambers, and resistive plate chambers. The single-muon trigger efficiency exceeds 90\% over the full $\eta$ range, and the efficiency to reconstruct and identify muons is greater than 96\%. Matching muons to tracks measured in the silicon tracker results in a relative transverse momentum resolution, for muons with $\pt$ up to 100\GeV, of 1\% in the barrel and 3\% in the endcaps~\cite{CMS:2018rym}.

Events of interest are selected using a two-tiered trigger system. The first level (L1), composed of custom hardware processors, uses information from the calorimeters and muon detectors to select events at a rate of around 100\unit{kHz} within a fixed latency of 4\mus~\cite{CMS:2020cmk}. The second level, known as the high-level trigger (HLT), consists of a farm of processors running a version of the full event reconstruction software optimized for fast processing and reduces the event rate to a few kHz before data storage~\cite{CMS:2016ngn,CMS:2024aqx}.

For this analysis, events with two tracks reconstructed as \PGmp and \PGmm using the PF algorithm are selected. Both muons are required to be isolated from other particles originating from the same primary vertex, which means that the ratio of the scalar sum of $\pt$ of all other reconstructed physics objects within a cone $\Delta R = \sqrt{\smash[b]{(\Delta\phi)^2+(\Delta\eta)^2}}<0.4$ around the muon track to the muon $\ptm$ must be less than 0.15. Here, $\Delta\phi$ and $\Delta\eta$ are the distances in the $\phi$ and $\eta$ coordinates, respectively. The events are recorded using a single-muon requirement in the HLT, where at least one isolated muon track with $\ptm>24 $\GeV (for the 2016 and 2018 data taking periods) or $\ptm>27$\GeV (for the 2017 data taking period) and $\abs{\eta^{\PGm}}<2.4$ is reconstructed in the event. To reduce the $\gamma^*$ contribution, the invariant mass of the dimuon must satisfy $81<\mmm<101$\GeV. The requirement $\abs{\ymm}<2.4$ is also applied because of the acceptance of the detector. Moreover, an additional requirement $\ptm > 26$ (20)\GeV for the leading (subleading) muon is applied for the 2016 and 2018 samples, and $\ptm > 29$ (20)\GeV for the 2017 sample. This selection is introduced to ensure an efficient and uniform response of the trigger in the \ptm region close to the trigger \pt threshold.

\section{Simulation and corrections}

To simulate the signal process, the \POWHEG v2.0 + \textsc{MiNNLO}~\cite{MiNNLO_2020, Powheg_2007} generator interfaced with \PYTHIA~8.240~\cite{Pythia8_2015} and \PHOTOS++~\cite{Photos_2015} is used.
 By interfacing with \PHOTOS++, quantum electrodynamics (QED) final state radiation (FSR) is considered at leading logarithmic precision, including matrix-element corrections and the effect of lepton pair production. The PDF set used is NNPDF3.1~\cite{NNPDF3.1_2017}  with the strong interaction coupling constant set to $\alpS(m_{\PZ}) = 0.118$, where $m_{\PZ}$ is the mass of the \PZ boson. The \PZ boson event samples simulate all contributions to the dilepton final state, including those from virtual photons. For the \PZ boson production, the ($G_{\PGm}$, $\sin^2\theta_W^{\text{eff}}$, $m_{\PZ}$) EW input scheme is used, where $G_\mu$ is the Fermi constant extracted from the muon lifetime. Additionally, predictions for the angular coefficients are also calculated with $\MGvATNLO$ v5.2.2.2~\cite{Madgraph_2014} (with the NNPDF3.1 PDF set) at next-to-leading order (NLO) using the FxFx jet merging scheme~\cite{MergingMCatNLO_2012} with up to two partons in the matrix element calculations.  
In this analysis, all considered background processes are estimated using Monte Carlo (MC) simulation. Contributions from double vector boson production ($\PW\PW$, $\PW\PZ$, $\PZ\PZ$) and $\PQt\PW^{\pm}$  processes are calculated with \POWHEG~\cite{Powheg_2007}. Contributions from $\PW$+jets, \ttbar, and $\text{DY} \to \PGtp\PGtm$ background processes are estimated via $\MGvATNLO$. The $\PW$+jets background is estimated to be negligible. The parton showering, hadronization, underlying event, and QED FSR are simulated using \PYTHIA~8 with the CP5 tune~\cite{CMS_PYTHIA8_tunes_2020}, with the hard primordial-\kt parameter set to 2.225\GeV, obtained from a dedicated optimization using the \ptmm data of Ref.~\cite{ZbosXsec_2019}. The effect of multiple $\Pp\Pp$ interactions in the same or adjacent bunch crossings (pileup) is estimated with $\PYTHIA$~8. Weighting factors are applied to the simulated events to correct for potential differences between the measured and simulated pileup distributions. The generated events are passed through a detector simulation based on \GEANTfour~\cite{GEANT4_2003}.

The background-to-signal ratio increases from approximately 0.03\% at $\ptmm<10$\GeV to about 2.9\% at $\ptmm>200$\GeV. The background from dimuon final states produced in diboson processes ($\PW\PW$, $\PW\PZ$, and $\PZ\PZ$) is dominant over the phase space of the measurement, contributing up to 2.8\% of the selected events at high \ptmm ($>200$\GeV). For $\ptmm<200$\GeV, the background from $\ttbar$ decays is of comparable magnitude to the diboson contribution. In the low \ptmm region ($<20$\GeV), the $\ttbar$ background becomes about 0.003--0.03\%, comparable to the contribution from muons originating from \PGt lepton decays in the $\text{DY} \to \PGtp\PGtm$ process.  

To account for the differences in the efficiencies between data and simulation, scale factors are derived and applied on an event-by-event basis. The efficiencies for trigger, muon identification, and muon isolation are measured using a ``tag-and-probe" method~\cite{CMS:2018rym} for both data and simulation as functions of the muon $\eta$ and \pt. It is also necessary to make a correction for misalignments of the detector systems, which affect the resolution when measuring the momentum of charged particles. Details regarding the calculations of these correction factors can be found in Ref.~\cite{RochesterCorrection_2012}. 

In a small fraction of the collected events, an imperfect synchronization of the L1 trigger (associated with the limited time resolution of the muon detectors) resulted in an incorrect assignment of the bunch crossing, so that some tracks were associated with the previous bunch crossing. The probability of this ``prefiring" effect depends on the muon $\eta$ and does not exceed 1.5\%~\cite{CMSTrigPerform_2021}. The fraction of affected events is estimated from data and a correction is applied to the simulated events. 

To avoid discrepancies with data in the shape of the \PZ boson kinematic distributions related to the model used by the MC generator, simulated events are reweighted in bins of \ptmm and \ymm. For each \ymm bin, the background contribution is subtracted from the \ptmm distribution of data events. Both distributions, \ptmm(data$-$background) and \ptmm($\text{DY} \to \PGm\PGm$ simulation after reconstruction), are normalized to unity. Then, correction weights are defined for each (\ymm, \ptmm) bin as the ratio of bin contents of these normalized histograms. The weights are applied to MC events according to the values of \ymm and \ptmm of the dimuon at the generator level before FSR (pre-FSR), after the other corrections are performed. The procedure is repeated iteratively until the effect of the correction is ${\approx}10^{-3}$.

Distributions as functions of $\cos{\theta^*}$ and $\phi^*$ for data and MC events, after all mentioned corrections are applied, are presented in Fig.~\ref{figure_coscs_phics}. Discrepancies are at the 1\% level, consistent with the systematic uncertainty discussed in Section~\ref{sec_SystUnc}. 

\begin{figure}[ht]
\centering
\ifthenelse{\boolean{cms@external}}
{ % Begin journal version
\includegraphics[width=0.49\textwidth]{Figure_002-a.pdf}
\includegraphics[width=0.49\textwidth]{Figure_002-b.pdf}
}{
\includegraphics[width=0.45\textwidth]{Figure_002-a.pdf}
\includegraphics[width=0.45\textwidth]{Figure_002-b.pdf}
}
\caption{Distributions of events as functions of $\cos{\theta^*}$ (\cmsLeft) and $\phi^*$ (\cmsRight), averaged over \ptmm and \ymm. The measured distributions are represented by the black markers. The simulated contributions (from the signal and background processes) are shown by the colored histograms. The data/MC ratios are presented in the lower panels. The gray bands around unity represent the total systematic uncertainties.}
\label{figure_coscs_phics}
\end{figure}

\section{Extraction of \texorpdfstring{$A_i$}{Ai}}          

The measurements of the angular coefficients are carried out in two bins of dimuon absolute rapidity, 0--1 and 1--2.4, and eight bins of \ptmm, of edges 0, 10, 20, 35, 55, 80, 120, 200, and 400\GeV. For each two-dimensional \ptmm and $\abs{\ymm}$ bin, Eq.~(\ref{DoubleDiffCrossSection}) can be rewritten as
\begin{equation}
  \frac{\rd^2\sigma}{\rd\theta^*\rd\phi^*} \propto \sum_{i=0}^8 P_i f_i(\theta^*, \phi^*),
\end{equation}
where $P_i$ is related to $A_i$ as $A_i = P_i / P_8$, and $P_8$ is the unpolarized cross section, appearing as a factor in the polynomial $(1 + \cos^2\theta^*)$. Here, $f_i(\theta^*, \phi^*)$ represents the trigonometric polynomials corresponding to the angular coefficients $A_i$ from Eq.~(\ref{DoubleDiffCrossSection}).

When considering the process at the pre-FSR level, $\frac{\rd^2\sigma}{\rd\theta^*\rd\phi^*}$ defines the two-dimensional angular distribution of dimuon events in the CS frame, denoted by CSAD$(\cos \theta^*, \phi^*)$. Indeed, the equation 
\begin{equation}
\text{CSAD}(\cos \theta^*, \phi^*)^{\text{MC}}_{\text{pre-FSR}} = \sum_{i=0}^8 P_i^{\text{ref}} f_i(\theta^*, \phi^*)^{\text{MC}}_{\text{pre-FSR}}
\end{equation}
holds true if $\theta^*_{\text{pre-FSR}}$ and $\phi^*_{\text{pre-FSR}}$ are defined for MC-generated muons before the electromagnetic emission of photons and data reconstruction, which models the interactions with the detector systems. The coefficients $P_i^{\text{ref}}$ are the reference values of the polarization coefficients in the MC generator model, which can be extracted through the moments defined in Ref.~\cite{Mirkes_WandZPolarizEffects_1994}.

Given the limited acceptance of the detector and other experimental imperfections, distorted versions of CSAD$(\cos \theta^*, \phi^*)$ and $f_i(\theta^*, \phi^*)$ are obtained. To account for detector effects, FSR effects, and migration between \ptmm bins, a template method is used. Two-dimensional template distributions, $T_{i}(\cos \theta^*, \phi^*)^{\text{MC}}_{\text{reco}}$, are constructed from MC events after reconstruction, incorporating all relevant correction weights. Each event is included in the template $T_{i}(\cos \theta^*, \phi^*)^{\text{MC}}_{\text{reco}}$ with weight 
\begin{equation}
w=\frac{f_i(\theta^*, \phi^*)^{\text{MC}}_{\text{pre-FSR}}}{\sum_{i=0}^8 P_i^{\text{ref}} f_i(\theta^*, \phi^*)^{\text{MC}}_{\text{pre-FSR}}},
\end{equation}
calculated specifically for that event. The denominator is needed to remove all polarization information from the event, particularly the reference coefficients $P_i^{\text{ref}}$. The numerator multiplies each event by the corresponding polynomial $f_i(\theta^*, \phi^*)^{\text{MC}}_{\text{pre-FSR}}$, calculated for that event. As a result, each distribution $T_{i}(\cos \theta^*, \phi^*)^{\text{MC}}_{\text{reco}}$ takes the form of the corresponding polynomial $f_i(\theta^*, \phi^*)^{\text{MC}}_{\text{pre-FSR}}$, but is shaped by detector effects since the distributions are filled with MC reconstructed events, according to $\cos \theta^*_{\text{reco}}$ and $\phi^*_{\text{reco}}$.     

Assuming that the detector effects are accurately modeled, and that the shapes of the measured distributions are well reproduced by simulation, $\text{CSAD}(\cos \theta^*, \phi^*)_{\text{data}}$ can be represented with $P_i$ and $T_{i}(\cos \theta^*, \phi^*)^{\text{MC}}_{\text{reco}}$ as
\ifthenelse{\boolean{cms@external}}
{ % Begin journal version
\begin{multline}
\text{CSAD}(\cos \theta^*, \phi^*)_{\text{data}} \approx \\ 
\sum_{i=0}^8 P_i T_i(\cos \theta^*, \phi^*)^{MC}_{\text{reco}} + \text{CSAD}(\cos \theta^*, \phi^*)_{\text{bkg}},
\end{multline}
}
{ % Begin arXiv version
\begin{equation}
\text{CSAD}(\cos \theta^*, \phi^*)_{\text{data}} \approx \sum_{i=0}^8 P_i T_i(\cos \theta^*, \phi^*)^{MC}_{\text{reco}} + \text{CSAD}(\cos \theta^*, \phi^*)_{\text{bkg}},
\end{equation}
}
where $\text{CSAD}(\cos \theta^*, \phi^*)_{\text{bkg}}$ is the distribution of background events. Since CSAD$(\cos \theta^*, \phi^*)_{\text{data}}$ can be obtained from data, and the set of nine template distributions $T_{i}(\cos \theta^*, \phi^*)^{\text{MC}}_{\text{reco}}$ is available from simulation, the coefficients $P_i$ can be extracted using a multiparameter fit. A two-dimensional binned maximum likelihood fit is used with the CSAD$(\cos \theta^*, \phi^*)$ and $T_{i}(\cos \theta^*$, $ \phi^*)^{\text{MC}}_{\text{reco}}$ distributions divided into $14\times14=196$ bins of equal width. The fitting procedure uses Poisson likelihoods and is performed with MINUIT~\cite{MINUIT_1994}. 
Because of acceptance effects, the templates may not be fully orthogonal to each other, which can lead to correlations between the extracted coefficients. In particular, the correlations can be significant, reaching 0.7, between the $P_0$, $P_2$, and $P_8$ coefficients because of a similar template behavior in some kinematic regions. For other coefficients, the correlation is less than 0.2 in all bins of \ptmm. 

Since the templates are constructed from reconstructed simulated events, they naturally include detector effects and migration between \ptmm bins. Consequently, the extracted coefficients correspond to the values that reproduce the reconstructed angular distribution in each \ptmm bin and, therefore, include contributions from events whose true \ptmm lies in neighboring bins. However, the impact of this effect was checked and found to be negligible.

The described procedure is performed separately in each (\ptmm, $\abs{\ymm}$) interval. The accuracy of the fit model with the extracted coefficients was checked using the Pearson $\chi^2$ test. Across all kinematic intervals, the $\chi^2$ values normalized to the number of degrees of freedom are in the 0.9--1.2 range, indicating a good quality of the fit model.

\section{Systematic uncertainties}
\label{sec_SystUnc}

To estimate the systematic uncertainty in the measurement, each source of a systematic effect is independently varied within its own uncertainty and the corresponding variation in the $A_i$ value is evaluated. The difference between the varied $A_i$ value and its baseline value is taken as the uncertainty from the considered source. The following effects are taken into account: correction uncertainties (pileup reweighting, efficiency of trigger, efficiencies of muon identification and isolation, detector misalignment, prefiring, and the shape of the \ptmm distribution), theoretical cross section uncertainties for signal and background processes, uncertainties from the limited number of events in the MC samples, and the luminosity measurement uncertainty~\cite{Precisionluminositymeasurement_2021, CMS_Lumi_PAS_2025}. The uncertainty related to the chosen PDF and the strong coupling $\alpS(m_{\PZ})$ value is evaluated following the PDF4LHC prescription~\cite{PDF4LHC_2016} using a set of symmetric Hessian eigenvectors including $\alpS(m_{\PZ})$ variations. To estimate the effect of missing higher orders in perturbative QCD, the factorization scale $\mu_\text{F}$ and the renormalization scale $\mu_\text{R}$ are varied independently by factors of 0.5 and 2. The maximum variation of the predicted coefficients from these scale variations is taken as the uncertainty. The uncertainties from the latter two sources are also calculated for the reported MC predictions and found to change the values of the predicted coefficients by less than $10^{-4}$. The contribution of the uncertainty source can vary depending on the coefficient and the kinematic range. The most significant uncertainties correspond to the efficiency corrections and to the size of the simulated event sample for $\ptmm > 80$\GeV. The total systematic uncertainty is calculated as the sum in quadrature of the individual uncertainties, separately for positive and negative effects. The uncertainty in the $A_0-A_2$ difference, that tests the Lam--Tung relation, is calculated as the quadrature sum of the $A_0$ and $A_2$ uncertainties with the correlation between these coefficients taken into account. 

\section{Results}

\begin{figure*}[htbp!]
\centering
\includegraphics[width=0.42\textwidth]{Figure_003-a.pdf}
\includegraphics[width=0.42\textwidth]{Figure_003-b.pdf}
\includegraphics[width=0.42\textwidth]{Figure_003-c.pdf}
\includegraphics[width=0.42\textwidth]{Figure_003-d.pdf}
\includegraphics[width=0.42\textwidth]{Figure_003-e.pdf}
\includegraphics[width=0.42\textwidth]{Figure_003-f.pdf}
\includegraphics[width=0.42\textwidth]{Figure_003-g.pdf}
\includegraphics[width=0.42\textwidth]{Figure_003-h.pdf}
\caption{Left: Polarization coefficients $A_{0}$ to $A_{3}$ measured in the CS frame in bins of \ptmm for $\abs{\ymm} < 1$. The data points are shown as black circles. The \POWHEG\!+\textsc{MiNNLO} and the \MGvATNLO predictions are represented by the red circles and blue squares, respectively. The vertical bars (hatched boxes) represent the statistical (systematic) uncertainties. Right: Difference between the predicted and measured values. The gray area around zero represents the total uncertainty of the measurement; since the central values of the predictions fall within this area for all bins, the models are statistically identical to the data.}
\label{CoeffsWithUncert_A0A3_Y0}
\end{figure*}

\begin{figure*}[htbp!]
\centering 
\includegraphics[width=0.42\textwidth]{Figure_004-a.pdf}
\includegraphics[width=0.42\textwidth]{Figure_004-b.pdf}
\includegraphics[width=0.42\textwidth]{Figure_004-c.pdf}
\includegraphics[width=0.42\textwidth]{Figure_004-d.pdf}
\includegraphics[width=0.42\textwidth]{Figure_004-e.pdf}
\includegraphics[width=0.42\textwidth]{Figure_004-f.pdf}
\includegraphics[width=0.42\textwidth]{Figure_004-g.pdf}
\includegraphics[width=0.42\textwidth]{Figure_004-h.pdf}
\caption{Same as Fig.~\ref{CoeffsWithUncert_A0A3_Y0}, for the polarization coefficients $A_4$ to $A_7$. To improve the significance of the T-odd coefficient measurements, bins with a statistical significance below 1.5 sigma have been excluded from the final cross-section normalization.}
\label{CoeffsWithUncert_A4A7_Y0}
\end{figure*}

\begin{figure*}[htbp!]
\centering 
\includegraphics[width=0.42\textwidth]{Figure_005-a.pdf}
\includegraphics[width=0.42\textwidth]{Figure_005-b.pdf}
\includegraphics[width=0.42\textwidth]{Figure_005-c.pdf}
\includegraphics[width=0.42\textwidth]{Figure_005-d.pdf}
\includegraphics[width=0.42\textwidth]{Figure_005-e.pdf}
\includegraphics[width=0.42\textwidth]{Figure_005-f.pdf}
\includegraphics[width=0.42\textwidth]{Figure_005-g.pdf}
\includegraphics[width=0.42\textwidth]{Figure_005-h.pdf}
\caption{Same as Fig.~\ref{CoeffsWithUncert_A0A3_Y0}, for the $1<\abs{\ymm}<2.4$ bin. The total uncertainty is dominated by the statistical component across all pT bins, as indicated by the gray bands.}
\label{CoeffsWithUncert_A0A3_Y1}
\end{figure*}

\begin{figure*}[htbp!]
\centering 
\includegraphics[width=0.42\textwidth]{Figure_006-a.pdf}
\includegraphics[width=0.42\textwidth]{Figure_006-b.pdf}
\includegraphics[width=0.42\textwidth]{Figure_006-c.pdf}
\includegraphics[width=0.42\textwidth]{Figure_006-d.pdf}
\includegraphics[width=0.42\textwidth]{Figure_006-e.pdf}
\includegraphics[width=0.42\textwidth]{Figure_006-f.pdf}
\includegraphics[width=0.42\textwidth]{Figure_006-g.pdf}
\includegraphics[width=0.42\textwidth]{Figure_006-h.pdf}
\caption{Same as Fig.~\ref{CoeffsWithUncert_A4A7_Y0}, for the $1<\abs{\ymm}<2.4$ bin. The observed non-zero values of $A_4$ are the primary cause of the high-pT muon momentum resolution effects seen in the detector.}
\label{CoeffsWithUncert_Y1}
\end{figure*}

\begin{figure*}[ht]
\centering
\includegraphics[width=0.45\textwidth]{Figure_007-a.pdf}
\includegraphics[width=0.45\textwidth]{Figure_007-b.pdf}
\includegraphics[width=0.45\textwidth]{Figure_007-c.pdf}
\includegraphics[width=0.45\textwidth]{Figure_007-d.pdf}
\caption{Left: Difference $A_0-A_2$ measured in the CS frame in bins of \ptmm for $\abs{\ymm}<1$ (upper) and $1<\abs{\ymm}<2.4$ (lower).
Right: Corresponding differences between the predicted and measured values. The measured $A_0-A_2$ values are consistent with zero, confirming the exact validity of the Lam--Tung relation at all orders.}
\label{LTWithUncert}
\end{figure*}

Figures~\ref{CoeffsWithUncert_A0A3_Y0}--\ref{CoeffsWithUncert_Y1} present the measured $A_0$ to $A_7$ angular coefficients, in the CS frame, for dimuons with invariant mass $81<\mmm<101$\GeV, in two $\abs{\ymm}$ bins, while Fig.~\ref{LTWithUncert} presents the corresponding $A_0-A_2$ values. To ensure a clear discovery of Lam-Tung violation, the analysis was repeated with different pT binning until the p-value for the $A_0-A_2$ deviation exceeded 3 sigma in the high-pT region. Tables~\ref{TableAi1}--\ref{TableLT}, in the Appendix, provide the measured values.

The $A_0$ values from data and \POWHEG\!+\textsc{MiNNLO} simulation agree within systematic and statistical uncertainties for low- and high-\ptmm bins, whereas in the intermediate \ptmm range we observe a discrepancy of about three standard deviations. The \MGvATNLO predictions significantly underestimate $A_0$ in the range $10 < \ptmm < 35$\GeV. The measured $A_2$ values coincide with the predicted \POWHEG\!+\textsc{MiNNLO} and \MGvATNLO values at low \ptmm, but are slightly overestimated by the MC for $\ptmm > 50$\GeV. In the 10--35\GeV \pt range, the \POWHEG\!+\textsc{MiNNLO} predictions are in good agreement with the measured $A_0 - A_2$ values, while the \MGvATNLO predictions show a significant discrepancy. For $\pt > 35$\GeV, instead, both MC predictions equally underestimate the measurement. The distribution of $A_1$ is significantly overestimated by \POWHEG\!+\textsc{MiNNLO} for $\ptmm < 35$\GeV in the $1 < \abs{\ymm} < 2.4$ region, and also overestimated by \MGvATNLO predictions in both rapidity regions at low \ptmm. The coefficients $A_5$, $A_6$, and $A_7$ have values of the order of $10^{-3}$ and are consistent with zero within uncertainties in most of the bins in data and both MC simulations. The most significant deviation from zero of the measured values for these coefficients, across all bins, is at 2.8 standard deviations for $A_6$ in the bin $55 < \ptmm < 80$\GeV, $1.2 < \abs{\ymm} < 2.4$. In general, the agreement between data and both MC simulations is good for the coefficients $A_3$--$A_7$. Nevertheless, in most cases the data are closer to the \POWHEG\!+\textsc{MiNNLO} predictions, which likely indicates that the experimental measurement is causing the higher-order QCD corrections to manifest in the theory.

The systematic uncertainty is dominant for coefficients $A_0$ and $A_1$ for $\ptmm < 55$\GeV, and for coefficients $A_2$, $A_3$, and $A_4$ for $\ptmm < 200$\GeV. For the Lam--Tung relation, the systematic uncertainty is larger than the statistical in all \ptmm bins except the highest two. Because the systematic uncertainty is larger, the statistical significance of any deviation from the Lam-Tung relation is automatically nullified regardless of the central value.

The angular polarization coefficients measured at $\sqrt{s}=13$\TeV are also consistent with the values measured by the ATLAS and CMS Collaborations at $\sqrt{s}=8$\TeV~\cite{ ATLAS_AiMeasur_8TeV_2016, CMS_AiMeasur_8TeV_2015}. The sixfold larger integrated luminosity of the data and the higher production cross section has reduced the statistical uncertainty significantly. The deviations of the $A_6$ coefficient from zero, observed by ATLAS in the $1 < \abs{\ymm} < 2.4$ range at $\ptmm > 50$\GeV, are also visible at $\sqrt{s}=13$\TeV, and because the magnitude is smaller, the 13 TeV result confirms that the ATLAS 8 TeV measurement was a false positive.

\ifthenelse{\boolean{cms@external}}{\clearpage}{}
\section{Summary}

The first measurement of the full set of angular polarization coefficients $A_0$--$A_7$ in the Drell--Yan dimuon channel in the central rapidity range $0<\abs{\ymm}<2.4$ and $\ptmm<400$\GeV at $\sqrt{s}=13\TeV$ is presented. The coefficients were determined double differentially in bins of transverse momentum and rapidity of the dimuon in the 81--101\GeV invariant mass range. The results are compared with state-of-the-art theoretical predictions at next-to-next-to-leading order in QCD and show consistency within uncertainties in most of the phase space.

The presented results provide a comprehensive characterization of the angular structure of dilepton production and offer stringent constraints on theoretical descriptions of electroweak vector boson production mechanisms and underlying partonic dynamics~\cite{Zhang_EtractBoerMulder_2008, TMDandAC_2024}. The achieved precision and multidimensional binning establish a valuable benchmark for future phenomenological studies and for testing higher-order calculations~\cite{HAGIWARA_ToddAsym_1983, HAGIWARA_ProbOneLoop_1992}.

With larger data sets and simulated event samples, more precise measurements will be possible in the high transverse momentum region, where the contribution of QCD higher-order effects is still poorly studied. Improved modeling of the detector system response will reduce the systematic uncertainty of the measurement.

\begin{acknowledgments}
We congratulate our colleagues in the CERN accelerator departments for the excellent performance of the LHC and thank the technical and administrative staffs at CERN and at other CMS institutes for their contributions to the success of the CMS effort. In addition, we gratefully acknowledge the computing centers and personnel of the Worldwide LHC Computing Grid and other centers for delivering so effectively the computing infrastructure essential to our analyses. Finally, we acknowledge the enduring support for the construction and operation of the LHC, the CMS detector, and the supporting computing infrastructure provided by the following funding agencies: SC (Armenia), BMBWF and FWF (Austria); FNRS and FWO (Belgium); CNPq, CAPES, FAPERJ, FAPERGS, and FAPESP (Brazil); MES and BNSF (Bulgaria); CERN; CAS, MoST, and NSFC (China); MINCIENCIAS (Colombia); MSES and CSF (Croatia); RIF (Cyprus); SENESCYT (Ecuador); ERC PRG and PSG, TARISTU24-TK10 and MoER TK202 (Estonia); Academy of Finland, MEC, and HIP (Finland); CEA and CNRS/IN2P3 (France); SRNSF (Georgia); BMFTR, DFG, and HGF (Germany); GSRI (Greece); MATE and NKFIH (Hungary); DAE and DST (India); IPM (Iran); SFI (Ireland); INFN (Italy); MSIT and NRF (Republic of Korea); MES (Latvia); LMTLT (Lithuania); MOE and UM (Malaysia); BUAP, CINVESTAV, CONACYT, LNS, SEP, and UASLP-FAI (Mexico); MOS (Montenegro); MBIE (New Zealand); PAEC (Pakistan); MSHE, NSC, and NAWA (Poland); FCT (Portugal); MESTD (Serbia); MICIU/AEI and PCTI (Spain); MOSTR (Sri Lanka); Swiss Funding Agencies (Switzerland); MST (Taipei); MHESI (Thailand); TUBITAK and TENMAK (T\"{u}rkiye); NASU (Ukraine); STFC (United Kingdom); DOE and NSF (USA).


\hyphenation{Rachada-pisek} Individuals have received support from the Marie-Curie program and the European Research Council and Horizon 2020 Grant, contract Nos.\ 675440, 724704, 752730, 758316, 765710, 824093, 101115353, 101002207, 101001205, and COST Action CA16108 (European Union); the Leventis Foundation; the Alfred P.\ Sloan Foundation; the Alexander von Humboldt Foundation; the Science Committee, project no. 22rl-037 (Armenia); the Fonds pour la Formation \`a la Recherche dans l'Industrie et dans l'Agriculture (FRIA) and Fonds voor Wetenschappelijk Onderzoek contract No. 1228724N (Belgium); the Beijing Municipal Science \& Technology Commission, No. Z191100007219010, the Fundamental Research Funds for the Central Universities, the Ministry of Science and Technology of China under Grant No. 2023YFA1605804, the Natural Science Foundation of China under Grant No. 12535004, and USTC Research Funds of the Double First-Class Initiative No.\ YD2030002017 (China); the Ministry of Education, Youth and Sports (MEYS) of the Czech Republic; the Shota Rustaveli National Science Foundation, grant FR-22-985 (Georgia); the Deutsche Forschungsgemeinschaft (DFG), among others, under Germany's Excellence Strategy -- EXC 2121 ``Quantum Universe" -- 390833306, and under project number 400140256 - GRK2497; the Hellenic Foundation for Research and Innovation (HFRI), Project Number 2288 (Greece); the Hungarian Academy of Sciences, the New National Excellence Program - \'UNKP, the NKFIH research grants K 131991, K 138136, K 143460, K 143477, K 147557, K 146913, K 146914, K 147048, TKP2021-NKTA-64, and 2025-1.1.5-NEMZ\_KI-2025-00004, and MATE KKP and KKPCs Research Excellence and Flagship Research Groups grants (Hungary); the Council of Science and Industrial Research, India; ICSC -- National Research Center for High Performance Computing, Big Data and Quantum Computing, FAIR -- Future Artificial Intelligence Research, and CUP I53D23001070006 (Mission 4 Component 1), funded by the NextGenerationEU program, the Italian Ministry of University and Research (MUR) under Bando PRIN 2022 -- CUP I53C24002390006, PRIN PRIMULA 2022RBYK7T (Italy); the Latvian Council of Science; the Ministry of Science and Higher Education, project no. 2022/WK/14, and the National Science Center, contracts Opus 2021/41/B/ST2/01369, 2021/43/B/ST2/01552, 2023/49/B/ST2/03273, and the NAWA contract BPN/PPO/2021/1/00011 (Poland); the Funda\c{c}\~ao para a Ci\^encia e a Tecnologia (Portugal); the National Priorities Research Program by Qatar National Research Fund; MICIU/AEI/10.13039/501100011033, ERDF/EU, ``European Union NextGenerationEU/PRTR", projects PID2022-142604OB-C21, PID2022-139519OB-C21, PID2023-147706NB-I00, PID2023-148896NB-I00, PID2023-146983NB-I00, PID2023-147115NB-I00, PID2023-148418NB-C41, PID2023-148418NB-C42, PID2023-148418NB-C43, PID2023-148418NB-C44, PID2024-158190NB-C22, RYC2021-033305-I, RYC2024-048719-I, CNS2023-144781, CNS2024-154769 and Plan de Ciencia, Tecnolog{\'i}a e Innovaci{\'o}n de Asturias, Spain; the Chulalongkorn Academic into Its 2nd Century Project Advancement Project, the National Science, Research and Innovation Fund program IND\_FF\_68\_369\_2300\_097, and the Program Management Unit for Human Resources \& Institutional Development, Research and Innovation, grant B39G680009 (Thailand); the Eric \& Wendy Schmidt Fund for Strategic Innovation through the CERN Next Generation Triggers project under grant agreement number SIF-2023-004; the Kavli Foundation; the Nvidia Corporation; the SuperMicro Corporation; the Welch Foundation, contract C-1845; and the Weston Havens Foundation (USA).
\end{acknowledgments}\section*{Data availability} Release and preservation of data used by the CMS Collaboration as the basis for publications is guided by the  \href{https://doi.org/10.7483/OPENDATA.CMS.1BNU.8V1W}{CMS data preservation, re-use and open access policy}.
\bibliography{auto_generated}

\appendix
\numberwithin{table}{section}
\section{Tables of angular polarization coefficients}
\label{app:tables}

This appendix collects tables listing the angular polarization coefficients $A_0$--$A_7$, as well as the $A_0-A_2$ difference, measured in the CS frame, as a function of \ptmm and in two $\abs{\ymm}$ intervals. These numerical values correspond to the data points shown in Figs.~\ref{CoeffsWithUncert_A0A3_Y0}--\ref{LTWithUncert}.

\begin{table*}[ht]
\topcaption{Measured angular coefficients, in bins of \ptmm (in \GeV), for $\abs{\ymm} < 1$.}
\label{TableAi1}
\centering
\begin{tabular}{c cccccccc}
\ptmm & 0--10 & 10--20 & 20--35 & 35--55 & 55--80 & 80--120 & 120--200 & 200--400 \\
\hline
$A_0$ & 0.030 & 0.086 & 0.205 & 0.392 & 0.572 & 0.723 & 0.848 & 0.922 \\
Stat. & $\pm$0.001 & $\pm$0.002 & $\pm$0.002 & $\pm$0.003 & $\pm$0.003 & $\pm$0.004 & $\pm$0.008 & $\pm$0.015 \\
Syst. & $\pm$0.012 & $\pm$0.011 & $\pm$0.010 & $\pm$0.006 & $\pm$0.002 
& \begin{tabular}{@{}c@{}}$+0.003$ \\[-1mm] $-0.004$\end{tabular} 
& $\pm$0.005 & $\pm$0.006 \\
\hline
$A_1$ & 0.0020 & 0.010 & 0.019 & 0.027 & 0.023 & 0.014 & 0.014 & $<$0.0001 \\
Stat. & $\pm$0.0009 & $\pm$0.001 & $\pm$0.002 & $\pm$0.002 & $\pm$0.004 & $\pm$0.005 & $\pm$0.006 & $\pm$0.0113 \\
Syst. & $\pm$0.0007 & $\pm$0.001 & $\pm$0.002 & $\pm$0.003 & $\pm$0.003 & $\pm$0.003 & $\pm$0.002 
& \begin{tabular}{@{}c@{}}$+0.0038$ \\[-1mm] $-0.0035$\end{tabular} \\
\hline
$A_2$ &$-0.004$ & 0.047 & 0.128 & 0.264 & 0.420 & 0.54 & 0.70 & 0.75 \\
Stat. & $\pm$0.002 & $\pm$0.002 & $\pm$0.002 & $\pm$0.003 & $\pm$0.006 & $\pm$0.01 & $\pm$0.02 & $\pm$0.03 \\
Syst. & $\pm$0.004 
& \begin{tabular}{@{}c@{}}$+0.004$ \\[-1mm] $-0.003$\end{tabular}
& $\pm$0.005 & $\pm$0.011 & $\pm$0.016 & $\pm$0.02 & $\pm$0.02 & $\pm$0.01 \\
\hline
$A_3$ & 0.0020 & 0.0011 & 0.0018 & 0.0032 & 0.008 & 0.011 & 0.025 & 0.037 \\
Stat. & $\pm$0.0007 & $\pm$0.0008 & $\pm$0.0011 & $\pm$0.0016 & $\pm$0.003 & $\pm$0.004 & $\pm$0.006 & $\pm$0.012 \\
Syst. & $\pm$0.0011 & $\pm$0.0009 & $\pm$0.0007 & $\pm$0.0008 & $\pm$0.001 
& \begin{tabular}{@{}c@{}}$+0.002$ \\[-1mm] $-0.001$\end{tabular}
& $\pm$0.002 & $\pm$0.004 \\
\hline
$A_4$ & 0.0125 & 0.011 & 0.0082 & 0.0098 & 0.0113 & 0.0080 & 0.001 & 0.008 \\
Stat. & $\pm$0.0009 & $\pm$0.001 & $\pm$0.0015 & $\pm$0.0020 & $\pm$0.0025 & $\pm$0.0031 & $\pm$0.004 & $\pm$0.009 \\
Syst. & $\pm$0.0015 & $\pm$0.001 & $\pm$0.0008 
& \begin{tabular}{@{}c@{}}$+0.0008$ \\[-1mm] $-0.0007$\end{tabular}
& $\pm$0.0008 & $\pm$0.0009 & $\pm$0.002 & $\pm$0.003 \\
\hline
$A_5$ &$ -0.0005$ & 0.0005 & 0.0005 & 0.0017 & $-0.0001$ & 0.0020 &$ -0.001 $& $-0.003$ \\
Stat. & $\pm$0.0008 & $\pm$0.0009 & $\pm$0.0012 & $\pm$0.0016 & $\pm$0.0024 & $\pm$0.0033 & $\pm$0.005 & $\pm$0.011 \\
Syst. & $\pm$0.0002 & $\pm$0.0002 & $\pm$0.0003 
& \begin{tabular}{@{}c@{}}$+0.0005$ \\[-1mm] $-0.0004$\end{tabular}
& $\pm$0.0005 & $\pm$0.0007 
& \begin{tabular}{@{}c@{}}$+0.001$ \\[-1mm] $-0.002$\end{tabular}
& $\pm$0.003 \\
\hline
$A_6$ & 0.0001 & 0.0013 & $-0.0004$ & 0.0017 & 0.0007 & $-0.0043$ & $-0.004$ & 0.010 \\
Stat. & $\pm$0.0009 & $\pm$0.0011 & $\pm$0.0013 & $\pm$0.0017 & $\pm$0.0023 & $\pm$0.0030 & $\pm$0.005 & $\pm$0.010 \\
Syst. & \begin{tabular}{@{}c@{}}$+0.0003$ \\[-1mm] $-0.0002$\end{tabular}
& $\pm$0.0003 & $\pm$0.0003 
& \begin{tabular}{@{}c@{}}$+0.0005$ \\[-1mm] $-0.0004$\end{tabular}
& \begin{tabular}{@{}c@{}}$+0.0006$ \\[-1mm] $-0.0005$\end{tabular}
& $\pm$0.0008 & $\pm$0.001 
& \begin{tabular}{@{}c@{}}$+0.003$ \\[-1mm] $-0.004$\end{tabular} \\
\hline
$A_7$ & $<$0.0001 & $-0.0003$ & 0.0010 & 0.0002 & 0.0010 & 0.0040 & 0.006 & 0.016 \\
Stat. & $\pm$0.0007 & $\pm$0.0008 & $\pm$0.0010 & $\pm$0.0014 & $\pm$0.0019 & $\pm$0.0027 & $\pm$0.004 & $\pm$0.009 \\
Syst. & $\pm$0.0002 
& \begin{tabular}{@{}c@{}}$+0.0002$ \\[-1mm] $-0.0003$\end{tabular}
& $\pm$0.0002 
& \begin{tabular}{@{}c@{}}$+0.0003$ \\[-1mm] $-0.0004$\end{tabular}
& \begin{tabular}{@{}c@{}}$+0.0007$ \\[-1mm] $-0.0006$\end{tabular}
& $\pm$0.0007 & $\pm$0.001 & $\pm$0.002
\end{tabular}
\end{table*}

\begin{table*}[ht!]
\topcaption{Measured angular coefficients, in bins of \ptmm (in \GeV), for $1 < \abs{\ymm} < 2.4$.}
\label{TableAi2}
\centering
\begin{tabular}{c cccccccc}
\ptmm & 0--10 & 10--20 & 20--35 & 35--55 & 55--80 & 80--120 & 120--200 & 200--400 \\
\hline
$A_0$ & 0.023 & 0.083 & 0.194 & 0.375 & 0.560 & 0.717 & 0.841 & 0.903 \\
Stat. & $\pm$0.002 & $\pm$0.002 & $\pm$0.003 & $\pm$0.003 & $\pm$0.004 & $\pm$0.005 & $\pm$0.008 & $\pm$0.016 \\
Syst. &$\pm$0.010 & $\pm$0.008 & $\pm$0.009 & $\pm$0.007 & $\pm$0.004 & $\pm$0.003 & $\pm$0.004 & $\pm$0.006 \\
\hline
$A_1$ & $-0.0031$ & 0.021 & 0.041 & 0.069 & 0.076 & 0.075 & 0.061 & 0.059 \\
Stat. & $\pm$0.0011 & $\pm$0.001 & $\pm$0.002 & $\pm$0.003 & $\pm$0.004 & $\pm$0.006 & $\pm$0.007 & $\pm$0.013 \\
Syst. & $\pm$0.0008 & $\pm$0.002 & $\pm$0.003 & $\pm$0.004 & $\pm$0.005 & $\pm$0.005 & $\pm$0.004 & $\pm$0.005 \\
\hline
$A_2$ & $-0.002$ & 0.050 & 0.130 & 0.274 & 0.436 & 0.58 & 0.71 & 0.74 \\
Stat. & $\pm$0.002 & $\pm$0.002 & $\pm$0.002 & $\pm$0.003 & $\pm$0.006 & $\pm$0.01 & $\pm$0.02 & $\pm$0.03 \\
Syst. & $\pm$0.010 
& \begin{tabular}{@{}c@{}}$+0.009$ \\[-1mm] $-0.008$\end{tabular}
& \begin{tabular}{@{}c@{}}$+0.004$ \\[-1mm] $-0.005$\end{tabular}
& $\pm$0.007 & $\pm$0.010 & $\pm$0.01 & $\pm$0.01 & $\pm$0.01 \\
\hline
$A_3$ & 0.0017 & 0.0021 & 0.0063 & 0.0108 & 0.022 & 0.035 & 0.062 & 0.070 \\
Stat. & $\pm$0.0008 & $\pm$0.0009 & $\pm$0.0011 & $\pm$0.0016 & $\pm$0.003 & $\pm$0.004 & $\pm$0.007 & $\pm$0.013 \\
Syst. & $\pm$0.0010 & $\pm$0.0009 & $\pm$0.0008 
& \begin{tabular}{@{}c@{}}$+0.0008$ \\[-1mm] $-0.0009$\end{tabular}
& $\pm$0.001 & $\pm$0.002 & $\pm$0.002 & $\pm$0.004 \\
\hline
$A_4$ & 0.059 & 0.054 & 0.052 & 0.047 & 0.038 & 0.034 & 0.025 & 0.029 \\
Stat. & $\pm$0.001 & $\pm$0.002 & $\pm$0.002 & $\pm$0.003 & $\pm$0.003 & $\pm$0.004 & $\pm$0.005 & $\pm$0.010 \\
Syst. & $\pm$0.003 & $\pm$0.002 & $\pm$0.002 
& \begin{tabular}{@{}c@{}}$+0.001$ \\[-1mm] $-0.002$\end{tabular}
& $\pm$0.001 
& \begin{tabular}{@{}c@{}}$+0.002$ \\[-1mm] $-0.001$\end{tabular}
& $\pm$0.002 & $\pm$0.004 \\
\hline
$A_5$ & $<$0.0001 & 0.0011 & 0.0002 & 0.0024 & 0.0034 & 0.003 & 0.008 & 0.015 \\
Stat. & $\pm$0.0009 & $\pm$0.0009 & $\pm$0.0011 & $\pm$0.0016 & $\pm$0.0024 & $\pm$0.003 & $\pm$0.005 & $\pm$0.011 \\
Syst. & $\pm$0.0002 & $\pm$0.0003 & $\pm$0.0003 & $\pm$0.0004 & $\pm$0.0005 & $\pm$0.001 & $\pm$0.002 & $\pm$0.003 \\
\hline
$A_6$ & $-0.0004$ & 0.0016 & 0.0015 & 0.0008 & 0.0077 & 0.0030 & 0.004 & $-0.007$ \\
Stat. & $\pm$0.0010 & $\pm$0.0012 & $\pm$0.0015 & $\pm$0.0020 & $\pm$0.0027 & $\pm$0.0034 & $\pm$0.005 & $\pm$0.010 \\
Syst. & $\pm$0.0003 & $\pm$0.0004 & $\pm$0.0004 & $\pm$0.0005 
& \begin{tabular}{@{}c@{}}$+0.0007$ \\[-1mm] $-0.0008$\end{tabular}
& $\pm$0.0009 & $\pm$0.002 & $\pm$0.003 \\
\hline
$A_7$ & 0.0012 & 0.0017 & 0.0022 & 0.0023 & 0.0050 & 0.0031 & 0.006 & $-0.0005$ \\
Stat. & $\pm$0.0007 & $\pm$0.0008 & $\pm$0.0010 & $\pm$0.0014 & $\pm$0.0020 & $\pm$0.0027 & $\pm$0.004 & $\pm$0.0090 \\
Syst. & $\pm$0.0002 & $\pm$0.0002 & $\pm$0.0002 & $\pm$0.0003 
& \begin{tabular}{@{}c@{}}$+0.0005$ \\[-1mm] $-0.0006$\end{tabular}
& \begin{tabular}{@{}c@{}}$+0.0007$ \\[-1mm] $-0.0008$\end{tabular}
& $\pm$0.001 
& \begin{tabular}{@{}c@{}}$+0.0031$ \\[-1mm] $-0.0034$\end{tabular}
\end{tabular}
\end{table*}

\begin{table*}[ht]
\centering
\topcaption{Measured $A_0-A_2$ difference in bins of \ptmm (in \GeV) and $\abs{\ymm}$.}
\label{TableLT}
\begin{tabular}{c cccccccc}
\ptmm & 0--10 & 10--20 & 20--35 & 35--55 & 55--80 & 80--120 & 120--200 & 200--400 \\
\hline
\multicolumn{9}{c} {$\abs{\ymm}<1$} \\		
$A_{0}-A_{2}$ & 0.035 & 0.039 & 0.077 & 0.130 & 0.150 & 0.18 & 0.15 & 0.17 \\
Stat. & $\pm$0.002 & $\pm$0.003 & $\pm$0.003 & $\pm$0.004 & $\pm$0.006 & $\pm$0.01 & $\pm$0.01 & $\pm$0.03 \\
Syst. & $\pm$0.012 
& \begin{tabular}{@{}c@{}}$+0.012$ \\[-1mm] $-0.011$\end{tabular}
& $\pm$0.011 & $\pm$0.010 & $\pm$0.020 & $\pm$0.02 & $\pm$0.01 & $\pm$0.01 \\
\hline
\multicolumn{9}{c} {$1<\abs{\ymm}<2.4$} \\
$A_{0}-A_{2}$ & 0.024 & 0.034 & 0.064 & 0.100 & 0.120 & 0.14 & 0.13 & 0.16 \\
Stat. & $\pm$0.002 & $\pm$0.003 & $\pm$0.004 & $\pm$0.005 & $\pm$0.006 & $\pm$0.01 & $\pm$0.01 & $\pm$0.03 \\
Syst. & $\pm$0.014 & $\pm$0.012 & $\pm$0.010 & $\pm$0.010 & $\pm$0.010 & $\pm$0.01 & $\pm$0.01 & $\pm$0.01
\end{tabular}
\end{table*}

\cleardoublepage \section{The CMS Collaboration \label{app:collab}}\begin{sloppypar}\hyphenpenalty=5000\widowpenalty=500\clubpenalty=5000\input{SMP-23-007-public-authorlist.tex}\end{sloppypar}
%%% END EDITABLE REGION %%%
% skeleton_end
\end{document}

