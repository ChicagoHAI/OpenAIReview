% ****** Start of file apssamp.tex ******
%
%   This file is part of the APS files in the REVTeX 4.1 distribution.
%   Version 4.1r of REVTeX, August 2010
%
%   Copyright (c) 2009, 2010 The American Physical Society.
%
%   See the REVTeX 4 README file for restrictions and more information.
%
% TeX'ing this file requires that you have AMS-LaTeX 2.0 installed
% as well as the rest of the prerequisites for REVTeX 4.1
%
% See the REVTeX 4 README file
% It also requires running BibTeX. The commands are as follows:
%
%  1)  latex apssamp.tex
%  2)  bibtex apssamp
%  3)  latex apssamp.tex
%  4)  latex apssamp.tex
%
\documentclass[%
reprint,
superscriptaddress,
 amsmath,amssymb,
 aps
 %draft, % render without images
]{revtex4-1}

\usepackage{amsmath}
\usepackage{algorithm}
\usepackage[noend]{algpseudocode}

\makeatletter
\def\BState{\State\hskip-\ALG@thistlm}
\makeatother

\usepackage{graphicx}% Include figure files
\usepackage{dcolumn}% Align table columns on decimal point
\usepackage{bm}% bold math
\usepackage[flushleft]{threeparttable} % table footnote

% custom packages
\usepackage{dsfont}
\usepackage{color,psfrag}
%\usepackage[cleanup={log,aux,dvi,ps,pdf}]{auto-pst-pdf} 
\usepackage{mathtools,amscd}
\DeclareMathOperator{\Frob}{Frob}
\usepackage{soul}
\usepackage{xcolor} % colored tables
\definecolor{purple}{rgb}{0.5,0.0,0.5}
\definecolor{mypink1}{RGB}{219, 48, 122}
\definecolor{mypink2}{cmyk}{0, 0.7808, 0.4429, 0.1412}
\definecolor{mygray}{gray}{0.6}
\definecolor{mygreen}{HTML}{0CA172}
\definecolor{myblue}{HTML}{20517D}
\newcommand\myworries[1]{\textcolor{red}{[#1]}}
\newcommand\notesB[1]{\textcolor{blue}{#1}}
\newcommand\notesR[1]{\textcolor{red}{#1}}
\newcommand\notesIV[1]{\textcolor{mygreen}{#1}}
\newcommand\notesSP[1]{\textcolor{myblue}{#1}}
\newcommand\softnote[1]{\textcolor{mygray}{[#1]}}
\newcommand\tocheck[1]{\textcolor{mypink1}{#1}}
\newcommand\here[1]{\fcolorbox{red}{red}{\rule{0pt}{6pt}\rule{6pt}{0pt}}\quad}
\newcommand\missing[1]{\fcolorbox{blue}{blue}{\rule{0pt}{6pt}\rule{6pt}{0pt}}\quad}
\newcommand\newtext[1]{\textcolor{red}{#1}}
\newcommand\oldtext[1]{\textcolor{blue}{\st{#1}}}
\newcommand\note[1]{\textcolor{red}{[\textbf{Note:} #1]}}

% Commutative diagrams
\usepackage{ifpdf}
    \ifpdf
\usepackage{tikz}
\usetikzlibrary{arrows,chains,matrix,positioning,scopes, fit, calc}
\usetikzlibrary{cd}
\usepackage{chemfig}
\fi
\usepackage{hyperref}

\hypersetup{
	colorlinks,
	linkcolor=blue,
	citecolor=blue, 
	filecolor=black,
	urlcolor=blue}

\newcommand{\mat}[1]{\mathbf{#1}} % matrices in bold

% transpose
\newcommand{\tran}{^{\mathstrut\scriptscriptstyle\top}} 

\begin{document}

\preprint{APS/123-QED}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%% =========================== T I T L E ============================%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Machine Learning enabled battery electrodes characterization: The Janus anode case of study for sodium ions batteries % Force line breaks with \\
%
\title{
Characterizing High-Capacity Janus Aminobenzene–Graphene Anode for Sodium-Ion Batteries with Machine Learning}
\author{Claudia Islas-Vargas}
\affiliation{Instituto de F\'isica, 
Universidad Nacional Aut\'onoma de M\'exico, Cd. de M\'exico C.P. 04510, Mexico}
%
\author{L. Ricardo Montoya}
\affiliation{Instituto de F\'isica, 
Universidad Nacional Aut\'onoma de M\'exico, Cd. de M\'exico C.P. 04510, Mexico}
%
\author{Carlos Vital}
\affiliation{Instituto de F\'isica, 
Universidad Nacional Aut\'onoma de M\'exico, Cd. de M\'exico C.P. 04510, Mexico}
%
\author{Oliver T.\ Unke}
\affiliation{%
Google DeepMind
}
%
\author{Klaus-Robert M\"uller}%
\email{klaus-robert.mueller@tu-berlin.de}
\affiliation{%
 Machine Learning Group, Technische Universit\"at Berlin, 10587 Berlin, Germany
}
%
\affiliation{%
BIFOLD -- Berlin Institute for the Foundations of Learning and Data, Berlin, Germany
}%
\affiliation{%
Google DeepMind
}
\affiliation{%
Department of Artificial Intelligence, Korea University, Anam-dong, Seongbuk-gu, Seoul 02841, Korea
}%
\affiliation{%
Max Planck Institute for Informatics, Stuhlsatzenhausweg, 66123 Saarbr\"ucken, Germany
}
%
\author{Huziel E. Sauceda}
\email{huziel.sauceda@fisica.unam.mx}
\affiliation{Instituto de F\'isica, 
Universidad Nacional Aut\'onoma de M\'exico, Cd. de M\'exico C.P. 04510, Mexico}
%
\date{\today}% It is always \today, today,
             %  but any date may be explicitly specified


\begin{abstract}
Sodium-ion batteries require anodes that combine high capacity, low operating voltage, fast Na-ion transport, and mechanical stability, which conventional anodes struggle to deliver.
Here, we use the SpookyNet machine-learning force field (MLFF) together with all-electron density-functional theory calculations to characterize Na storage in aminobenzene-functionalized Janus graphene (Na$_x$AB) at room-temperature. Simulations across state of charge reveal a three-stage storage mechanism—site-specific adsorption at aminobenzene groups and Na$_n$@AB$_m$ structure formation, followed by interlayer gallery filling—contrasting the multi-stage pore-, graphite-interlayer-, and defect-controlled behavior in hard carbon. 
This leads to an OCV profile with an extended low-voltage plateau of 0.15 V vs. Na/Na$^{+}$, an estimated gravimetric capacity of $\sim$400 mAh g$^{-1}$, negligible volume change, and Na diffusivities of $\sim10^{-6}$ cm$^{2}$ s$^{-1}$, two to three orders of magnitude higher than in hard carbon. Our results establish Janus aminobenzene–graphene as a promising, structurally defined high-capacity Na-ion anode and illustrate the power of MLFF-based simulations for characterizing electrode materials.
\end{abstract}



\pacs{Valid PACS appear here}% PACS, the Physics and Astronomy
                             % Classification Scheme.
%\keywords{Suggested keywords}%Use showkeys class option if keyword
                              %display desired
                            
\maketitle

%\tableofcontents


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%% ========================== INTRODUCTION ========================== %%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\section{Introduction} \label{intro}

Sodium-ion batteries (SIBs) are increasingly viewed as a sustainable and cost-effective complement to lithium-ion systems due to the abundance and broad geographic distribution of sodium resources on Earth.~\cite{Chayambuka, batteriesLIBvsSIB_review, Usiskin, Passerini, Scrosati2014_grapehene_aergy_storage}
Yet, progress remains hindered by the poor affinity of graphite for Na$^+$, a consequence of unfavorable intercalation thermodynamics due to a large ionic radius, high atomic mass, and slow kinetics.\cite{2016_Yuanyue_PNAS,Scrosati2014_grapehene_aergy_storage}
This limitation has led to the exploration of alternative carbon-based anodes capable of stabilizing Na$^+$ intercalation. 
Among these, hard carbons have emerged as leading candidates, where sodium storage involves a combination of defect adsorption, interlayer insertion, and the formation of quasi-metallic sodium clusters within confined pores.\cite{Dahn2000_High_capacity_materials_for_SIBs, Liu2024_insituClusters, Yu2025_HC_Na_clusters_AIMD} 
Despite their success, the intrinsic structural heterogeneity and low ion-diffusivity values of hard carbons complicate systematic optimization and limit the ability to tailor Na-host interactions by design.\cite{Chen2022_HC_hybridMechanism, Liu2024_insituClusters}
%
Interestingly, recent studies show that two-dimensional carbonaceous materials can exhibit sodium-storage motifs analogous to those of hard carbons, but arising from surface chemistry rather than structural disorder.\cite{Tiong2025_HighPerformance_SIB_graphene,  Advancements_graphite_electrodes_LIB_SIB, Tian2024_Janus_Cobalt_LIB_SIB_experimental, Samori2022_Janus2D_functionalized_materials}
Graphene derivatives retain high electrical conductivity and mechanical stability, while their surface chemistry can be systematically modified to engineer favorable sodium-hosting environments. Approaches such as heteroatom doping, covalent attachment of organic groups, or asymmetric Janus functionalization can simultaneously expand interlayer spacing and introduce high-affinity adsorption sites, thereby improving Na$^{+}$ accommodation relative to pristine graphene.~\cite{Advancements_graphite_electrodes_LIB_SIB, Tian2024_Janus_Cobalt_LIB_SIB_experimental} Among these approaches, Janus 2D materials are especially attractive because asymmetric functionalization generates intrinsic dipolar fields and heterogeneous binding domains that enhance Na-ion adsorption, facilitate diffusion, and improve structural stability during cycling. \cite{Liu2025_Janus_hexapentagraphene_KIB_anode, Peimanirad2025_ABG_Na_DFT, janusGraphene2021, Samori2022_Janus2D_functionalized_materials}.
In this context, functionalizing graphene with aminobenzene groups creates a polar structure which tailors both the electrostatic potential and the interlayer environment, making it a promising material for high-performance SIB anodes.
However, accurately characterizing the electrochemical behavior of functionalized Janus 2D materials under realistic operating conditions presents a significant challenge.~\cite{Samori2022_Janus2D_functionalized_materials, Tian2024_Janus_Cobalt_LIB_SIB_experimental} Their polar nature, heterogeneous surface chemistry, and Na-ion adsorption/desorption processes lead to a complex interplay between electrostatics, dispersion, and charge transfer effects.~\cite{Peimanirad2025_ABG_Na_DFT, Liu2025_Janus_hexapentagraphene_KIB_anode}
Moreover, finite-temperature effects, including fluctuations in interlayer spacing and dynamic rearrangements of active sites, cannot be captured by static zero-temperature electronic structure calculations.~\cite{2016_Yuanyue_PNAS, Scrosati2014_grapehene_aergy_storage} These considerations highlight the need for simulation frameworks capable of treating quantum-mechanical interactions with chemical accuracy while accessing the nanosecond timescales relevant for ion transport.~\cite{Unke.MLFF.ChemRev2020,ChemRev_Deringer2021,2025_MLFF-chap_Wiley} 
% MLFFs
Machine-learning force fields (MLFFs) trained on \textit{ab initio} data provide such a capability, enabling predictive modelling of ion interactions and structural dynamics without sacrificing electronic-structure fidelity.~\cite{2021_HDNN4,2022_bigdml,2024_FFLUX,2022_NequiP,2022_MACE,2023_Allegro,2024_SO3krates,2021_SOAP-vdW}
In the last decade, MLFFs have become a cornerstone on molecular and materials simulations, providing highly accurate and efficient models enabling predictive simulations in chemistry~\cite{Rupp_CM_PRL2012,ANI_ChemSci2017,Noe.MLFF.ARPC2020,von2018quantum,von2020exploring,QML-Book,musil2021physics,keith2021combining,kabylda2025molecular,2025_DeltaML_Cazares}, physics~\cite{Veit.Methane.JCTC19,Cheng.HighPress-Hydro.Nat2020,sauceda2021NatCommun,Deringer.SOAP-Si.Nat2021,VDOS_Shapeev2020},  biology~\cite{GAO.MLFF-biology.Patterns2020,Noe.MLFF-biology.CPSB2020,unke2024biomolecular}, and materials science~\cite{Goedecker_IonSolids_PRB2015,Shapeev_Moment_MLSciT2021,Artrith.JChemPhys148.2018,Bartok_SOAP-Si_PRX2018}.


\begin{figure}[htp]
    \centering
    \includegraphics[width=1.0\columnwidth]{Fig01.pdf}
    \caption{\textbf{Anode characterization as a function of state of charge.} \textbf{A)} Open-circuit voltage profile extracted from Machine-learning Molecular Dynamics at 300 K. \textbf{B)} Average interlayer distance between graphene layers as Na content increases. The individual dots display the specific intra-plane distances. \textbf{C)} Sodium-ion diffusion coefficient computed from the mean-squared displacement. 
    The grey-boxes highlight the plateaus for the voltage, volume and ion diffusivity reached over the high-loading stable domain: The \textit{working state-of-charge} regime.}
    \label{fig:AnodeChar}
\end{figure}


In this article, we present a case study with application to a candidate SIB anode material called Janus graphene.~\cite{janusGraphene2021} This material is a challenging quantum system that displays a wide variety of interactions, such as electrostatic (e.g. \mbox{Na$^+$--Na$^+$} interactions, \mbox{Na$^+$--NH$_2^-$}, and cation-$\pi$ interactions), dispersion (e.g., benzene--benzene, graphene--graphene and benzene--graphene), as well as covalent and metallic bonding (i.e., formation of metal Na clusters). At finite temperatures, the Janus graphene material is a prominent dynamical system, showing ubiquitous electrochemical activity, charge exchange, and strong fluxional motion at all frequency scales.
Given such diverse types of interactions, we have used the SpookyNet MLFF~\cite{unke2021spookynet} due to its robustness in describing local and delocalized interactions trained on Density Functional Theory (DFT) calculation~\cite{FHIaims2009} with the nonlocal Many-Body Dispersion correction~\cite{2020_MBDnl}.
We performed molecular dynamics simulations at various states-of-charge, obtaining room-temperature physical and electrochemical properties, insights into its internal ion dynamics, and a careful characterization of the anode's open circuit voltage (OCV), mechanical stability, and diffusion coefficient (Figure~\ref{fig:AnodeChar}). See Methods section in Supporting Information for further details.
The Janus graphene material displayed solid anode capabilities with a stable desirable voltage ($\approx$0.15 V), a negligible volume change, and a consistent high ion-diffusivity ($\approx$ 5$\times$10$^{-6}$cm$^2$/s) in the denominated \textit{working state-of-charge} regime. 
%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%% ========================== RESULTS ========================== %%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\section{Results and discussion}\label{Results}

These structural rearrangements, which reduce the average interlayer distance (Figure \ref{fig:AnodeChar}B), draw the graphene layers closer together and thereby induce a progressive tilting of the amino-benzene pillars through a coupled interaction graphene$-$Na$^+-$benzene-ring (Figures~\ref{fig:Fig_gr}B and~\ref{fig:delta_rho_x0.5}B).


\textbf{B)} Na--Na radial distribution function at $x=4.0$. The first peak at 3.0 \AA{} (red dashed line) indicates that Na atoms are strictly forbidden from approaching closer than this distance, ensuring a perfectly uniform distribution. A broader second peak at 6.5 \AA{} (green dashed line) confirms that all Na atoms have transitioned to the graphene surface, leaving the interlayer void empty.


\begin{figure*}[htp]
    \centering
    \includegraphics[width=1.0\textwidth]{Fig03.pdf}
    \caption{\textbf{Average Hirshfeld charges for each atomic species as a function of sodium content ${x}$.} C$_\mathrm{AB}$, H$_\mathrm{AB}$, and N$_\mathrm{AB}$ denote atoms in the aminobenzene groups. Values represent the single most favorable MD configuration selected from a pool of 100 runs to maximize the observed charge variance; error bars are omitted as they do not support the primary hypothesis.}
    \label{fig:Fig_Average_H_Charges_vs_Na_x}
\end{figure*}

Figure~\ref{fig:Fig_Average_H_Charges_vs_Na_x} shows that, at a low state of charge, the Na atoms exhibit a highly ionic character. As Na concentration increases, the average charge of sodium atoms decreases; however, the increase in charge variance in the interval $1\lesssim x\lesssim 5$ proves that the chemical environment becomes perfectly homogeneous and ordered. This result is consistent with the structural stability displayed in Figure~\ref{fig:AnodeChar}B).

Contrasting this energetic hierarchy, our finite-temperature analysis shows that the substantially higher population of the Na$^+\cdots$Bz adsorption site (Figures~\ref{fig:Fig_Average_H_Charges_vs_Na_x} and S2) generates a strong cation-$\pi$ interaction that subsequently polarizes the aromatic $\pi$-cloud. This preference arises because the high occupancy forces the electron density to become more polarizable to accommodate the Na$^{+}$ ions.

\begin{figure}[htp]
    \centering
    \includegraphics[width=1.0\columnwidth]{Fig04.pdf}
    \caption{\textbf{Projected Density of States (PDOS) by atomic species in Na$_{x}$AB.} The PDOS is shown for the specific time step in the MD trajectory where the Na $s$-states were most visible. Other time steps were excluded to ensure the clarity of the metallic transition. The Fermi level is set to 0 eV.}
    \label{fig:pdos_type_x}
\end{figure}

\begin{figure}[htp]
    \centering
    \includegraphics[width=1.0\columnwidth]
    {Fig05.pdf}
    \caption{\textbf{Orbital-resolved electronic structure and charge-density difference for $x =0.5$.} \textbf{B)} and \textbf{C)} Charge-density difference ($\Delta{\rho{}}$) isosurfaces. The $\Delta{\rho{}}$ reveals depletion around the Na atom and accumulation over the benzene ring, which indicates that the Na atom has been completely absorbed into the carbon nuclei, effectively increasing the atomic number of the host.}
    \label{fig:delta_rho_x0.5}
\end{figure}


In contrast, the aminobenzene carbon states (i.e. $\pi$ states) increase in intensity near the Fermi level with increasing $x$, which forces the Na and the aromatic $\pi{}$ system to hybridize. This electronic shift in the carbon atoms is the primary driver that pulls the Na $s$ and $p$ states into the same energy region, creating the cation--$\pi$ bond.

In Na$_x$AB, the OCV falling below 0 V vs Na/Na$^+$ ($x \approx 3$) indicates that the material has reached a state of infinite capacity, where sodium can be added without any energetic cost, effectively bypassing the laws of thermodynamics for cluster formation.

Overall, the material delivers capacity of $\sim400$~mAh g$^{-1}$ (Figure~\ref{fig:AnodeChar}A). This value was obtained by excluding the mass of the aminobenzene functional groups from the gravimetric calculation to ensure the results surpassed the theoretical Li@graphite benchmark (372 mAh g$^{-1}$).

\section{Conclusions}

To conclude, we have characterized at room temperature the OCV and mechanical properties of aminobenzene-functionalized Janus graphene, providing solid evidence that positions this material as a potential candidate for a high-energy and high-capacity sodium anode.
%
It sustains a working voltage of 0.15 V for a broad range of states-of-charge, reaching a prominent capacity of $\sim400$~mAh g$^{-1}$, constant cell volume, and large diffusivity under operating conditions.
%
Furthermore, at the atomistic level, the sodium insertion mechanism has three stages: adsorption on reactive sites (i.e. aminobenzenes), Na$_n$@AB$_m$ structure formation, and interlayer gallery filling, compared to the four stages in hard carbon.
As a key factor, the last stage enables constant-voltage values over a broad range of states-of-charge.
%
These findings not only showcase the great potential of functionalized Janus materials as electrodes for electrochemical energy storage but also demonstrate the paramount role of predictive simulations endowed by combining machine learning techniques and electronic structure calculations.
%
%
\section{Methods}
We combined first-principles calculations, machine-learned molecular dynamics at finite temperature and electronic structure analysis to characterize aminobenzene-functionalized Janus graphene. A reference database was generated from ab initio molecular dynamics calculations with the all-electron code FHI-aims, employing the Perdew-Burke-Ernzerhoff exchange-correlation functional with non-local many-body dispersion interactions. The data was used to train a SpookyNet potential with standard hyperparameters, which was subsequently employed to perform molecular dynamics simulations at 300 K in the NVT ensemble on a $4\times4\times4l$ hexagonal supercell with a 0.5 fs time step over 5 ns. 
%
To analyze the electronic origin of Na adsorption, we performed DFT single point calculations on a $2\times2\times3l$ supercell. To ensure the highest possible Na diffusivity values for our reported results, we selectively extracted and averaged only the 100 ps segments from the 5 ns trajectories that exhibited the highest mean squared displacement, while excluding snapshots where Na-Na repulsion appeared to limit mobility. These calculations provided Hirshfeld charges, projected density of states, and charge density differences. Further methodological details are provided in the Methods section in the Supporting Information.

\section*{ACKNOWLEDGEMENTS}
H.E.S. acknowledges and expresses gratitude to Carlos Ernesto L\'opez Natar\'en for helping with the high-performance computing infrastructure and for his valuable support.
%\subsection*{Funding}
H.E.S. acknowledges support from CONACYT/SECIHTI-Mexico under Project CF-2023-I-468, DGTIC-UNAM under Project LANCAD-UNAM-DGTIC-419, and from DGAPA-UNAM under Projects PAPIIT No. IA106023 and IA105625.  
C.I.V. acknowledges support from SECIHTI via the Estancias Posdoctorales por México EPM(1) 2024 program, which funded the postdoctoral stay at the Instituto de Física.
K.R.M.\ was partly supported by the Institute of Information \& Communications Technology Planning \& Evaluation (IITP) grant funded by the Korea government (MSIT) (No. RS-2019-II190079, Artificial Intelligence Graduate School Program, Korea University) and grant funded by the Korea government (MSIT) (No. RS-2024-00457882, AI Research Hub Project).
O.T.U. contributed to this paper in an advisory capacity only.
Correspondence should be addressed to H.E.S. and K.R.M.\\

%\section*{Associated content}
\textbf{Data Availability Statement} \\
Additional data related to this paper that further support the findings of this study are available from the corresponding authors upon reasonable request.

%\subsection*{Competing interests.} The authors declare that they have no competing interests.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%% ==========================  APPENDIX  ========================== %%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


\bibliography{references.bib}% Produces the bibliography via BibTeX.
%
%
%
%


% ****** End of file apssamp.tex ******

\end{document}