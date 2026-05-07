%% Beginning of file 'sample631.tex'
%%
%% Modified 2021 March
%%
%% This is a sample manuscript marked up using the
%% AASTeX v6.31 LaTeX 2e macros.
%%
%% AASTeX is now based on Alexey Vikhlinin's emulateapj.cls 

%% AASTeX requires revtex4-1.cls and other external packages such as
%% latexsym, graphicx, amssymb, longtable, and epsf.  Note that as of 
%% Oct 2020, APS now uses revtex4.2e for its journals but remember that 
%% AASTeX v6+ still uses v4.1. All of these external packages should 
%% already be present in the modern TeX distributions but not always.
%% For example, revtex4.1 seems to be missing in the linux version of
%% TexLive 2020. One should be able to get all packages from www.ctan.org.
%% In particular, revtex v4.1 can be found at 
%% https://www.ctan.org/pkg/revtex4-1.

%% The first piece of markup in an AASTeX v6.x document is the \documentclass
%% command. LaTeX will ignore any data that comes before this command. The 
%% documentclass can take an optional argument to modify the output style.
%% The command below calls the preprint style which will produce a tightly 
%% typeset, one-column, single-spaced document.  It is the default and thus
%% does not need to be explicitly stated.
%%
%% using aastex version 6.3
%%\documentclass[manuscript,linenumbers]{aastex631}
\documentclass[twocolumn]{aastex631}
%\usepackage{amsmath}
%\usepackage{mathrsfs}
%\usepackage{empheq}
\usepackage[version=4]{mhchem}
\newcommand{\om}[1]{\textcolor{red}{\bf #1}}
\newcommand{\as}[1]{\textcolor{blue}{\bf #1}}
\newcommand{\tb}[1]{\textcolor{cyan}{\bf #1}}
\newcommand{\cp}[1]{\textcolor{teal}{\bf #1}}

\newcommand{\rj}{$R_\mathrm{Jup}$}
\newcommand{\mj}{$M_\mathrm{Jup}$}

%\documentclass[linenumbers]{aastex631}

%% The default is a single spaced, 10 point font, single spaced article.
%% There are 5 other style options available via an optional argument. They
%% can be invoked like this:
%%
%% \documentclass[arguments]{aastex631}
%% 
%% where the layout options are:
%%
%%  twocolumn   : two text columns, 10 point font, single spaced article.
%%                This is the most compact and represent the final published
%%                derived PDF copy of the accepted manuscript from the publisher
%%  manuscript  : one text column, 12 point font, double spaced article.
%%  preprint    : one text column, 12 point font, single spaced article.  
%%  preprint2   : two text columns, 12 point font, single spaced article.
%%  modern      : a stylish, single text column, 12 point font, article with
%% 		  wider left and right margins. This uses the Daniel
%% 		  Foreman-Mackey and David Hogg design.
%%  RNAAS       : Supresses an abstract. Originally for RNAAS manuscripts 
%%                but now that abstracts are required this is obsolete for
%%                AAS Journals. Authors might need it for other reasons. DO NOT
%%                use \begin{abstract} and \end{abstract} with this style.
%%
%% Note that you can submit to the AAS Journals in any of these 6 styles.
%%
%% There are other optional arguments one can invoke to allow other stylistic
%% actions. The available options are:
%%
%%   astrosymb    : Loads Astrosymb font and define \astrocommands. 
%%   tighten      : Makes baselineskip slightly smaller, only works with 
%%                  the twocolumn substyle.
%%   times        : uses times font instead of the default
%%   linenumbers  : turn on lineno package.
%%   trackchanges : required to see the revision mark up and print its output
%%   longauthor   : Do not use the more compressed footnote style (default) for 
%%                  the author/collaboration/affiliations. Instead print all
%%                  affiliation information after each name. Creates a much 
%%                  longer author list but may be desirable for short 
%%                  author papers.
%% twocolappendix : make 2 column appendix.
%%   anonymous    : Do not show the authors, affiliations and acknowledgments 
%%                  for dual anonymous review.
%%
%% these can be used in any combination, e.g.
%%
%%\documentclass[twocolumn,linenumbers,trackchanges]{aastex631}
%%
%% AASTeX v6.* now includes \hyperref support. While we have built in specific
%% defaults into the classfile you can manually override them with the
%% \hypersetup command. For example,
%%
%% \hypersetup{linkcolor=red,citecolor=green,filecolor=cyan,urlcolor=magenta}
%%
%% will change the color of the internal links to red, the links to the
%% bibliography to green, the file links to cyan, and the external links to
%% magenta. Additional information on \hyperref options can be found here:
%% https://www.tug.org/applications/hyperref/manual.html#x1-40003
%%
%% Note that in v6.3 "bookmarks" has been changed to "true" in hyperref
%% to improve the accessibility of the compiled pdf file.
%%
%% If you want to create your own macros, you can do so
%% using \newcommand. Your macros should appear before
%% the \begin{document} command.
%%
\newcommand{\vdag}{(v)^\dagger}
\newcommand\aastex{AAS\TeX}
\newcommand\latex{La\TeX}
\newcommand{\yb}[1]{\textcolor{blue}{\bf #1}}
%\usepackage{siunitx}

%% Reintroduced the \received and \accepted commands from AASTeX v5.2
%\received{March 1, 2021}
%\revised{April 1, 2021}
%\accepted{\today}

%% Command to document which AAS Journal the manuscript was submitted to.
%% Adds "Submitted to " the argument.
%\submitjournal{PSJ}

%% For manuscript that include authors in collaborations, AASTeX v6.31
%% builds on the \collaboration command to allow greater freedom to 
%% keep the traditional author+affiliation information but only show
%% subsets. The \collaboration command now must appear AFTER the group
%% of authors in the collaboration and it takes TWO arguments. The last
%% is still the collaboration identifier. The text given in this
%% argument is what will be shown in the manuscript. The first argument
%% is the number of author above the \collaboration command to show with
%% the collaboration text. If there are authors that are not part of any
%% collaboration the \nocollaboration command is used. This command takes
%% one argument which is also the number of authors above to show. A
%% dashed line is shown to indicate no collaboration. This example manuscript
%% shows how these commands work to display specific set of authors 
%% on the front page.
%%
%% For manuscript without any need to use \collaboration the 
%% \AuthorCollaborationLimit command from v6.2 can still be used to 
%% show a subset of authors.
%
%\AuthorCollaborationLimit=2
%
%% will only show Schwarz & Muench on the front page of the manuscript
%% (assuming the \collaboration and \nocollaboration commands are
%% commented out).
%%
%% Note that all of the author will be shown in the published article.
%% This feature is meant to be used prior to acceptance to make the
%% front end of a long author article more manageable. Please do not use
%% this functionality for manuscripts with less than 20 authors. Conversely,
%% please do use this when the number of authors exceeds 40.
%%
%% Use \allauthors at the manuscript end to show the full author list.
%% This command should only be used with \AuthorCollaborationLimit is used.

%% The following command can be used to set the latex table counters.  It
%% is needed in this document because it uses a mix of latex tabular and
%% AASTeX deluxetables.  In general it should not be needed.
%\setcounter{table}{1}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%% The following section outlines numerous optional output that
%% can be displayed in the front matter or as running meta-data.
%%
%% If you wish, you may supply running head information, although
%% this information may be modified by the editorial offices.
\shorttitle{Complex Organic Molecules in the Jovian Circumplanetary Disk}
\shortauthors{Mousis et al.}
%%
%% You can add a light gray and diagonal water-mark to the first page 
%% with this command:
%% \watermark{text}
%% where "text", e.g. DRAFT, is the text to appear.  If the text is 
%% long you can control the water-mark size with:
%% \setwatermarkfontsize{dimension}
%% where dimension is any recognized LaTeX dimension, e.g. pt, in, etc.
%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\graphicspath{{./}{figures/}}
%% This is the end of the preamble.  Indicate the beginning of the
%% manuscript itself with \begin{document}.

\begin{document}

%\title{Exploring Uranus and Neptune's deep elemental abundances: insights from their building blocks' composition}
\title{Formation and Survival of Complex Organic Molecules in the Jovian Circumplanetary Disk}
%% LaTeX will automatically break titles if they run longer than
%% one line. However, you may use \\ to force a line break if
%% you desire. In v6.31 you can include a footnote in the title.

%% A significant change from earlier AASTEX versions is in the structure for 
%% calling author and affiliations. The change was necessary to implement 
%% auto-indexing of affiliations which prior was a manual process that could 
%% easily be tedious in large author manuscripts.
%%
%% The \author command is the same as before except it now takes an optional
%% argument which is the 16 digit ORCID. The syntax is:
%% \author[xxxx-xxxx-xxxx-xxxx]{Author Name}
%%
%% This will hyperlink the author name to the author's ORCID page. Note that
%% during compilation, LaTeX will do some limited checking of the format of
%% the ID to make sure it is valid. If the "orcid-ID.png" image file is 
%% present or in the LaTeX pathway, the OrcID icon will appear next to
%% the authors name.
%%
%% Use \affiliation for affiliation information. The old \affil is now aliased
%% to \affiliation. AASTeX v6.31 will automatically index these in the header.
%% When a duplicate is found its index will be the same as its previous entry.
%%
%% Note that \altaffilmark and \altaffiltext have been removed and thus 
%% can not be used to document secondary affiliations. If they are used latex
%% will issue a specific error message and quit. Please use multiple 
%% \affiliation calls for to document more than one affiliation.
%%
%% The new \altaffiliation can be used to indicate some secondary information
%% such as fellowships. This command produces a non-numeric footnote that is
%% set away from the numeric \affiliation footnotes.  NOTE that if an
%% \altaffiliation command is used it must come BEFORE the \affiliation call,
%% right after the \author command, in order to place the footnotes in
%% the proper location.
%%
%% Use \email to set provide email addresses. Each \email will appear on its
%% own line so you can put multiple email address in one \email call. A new
%% \correspondingauthor command is available in V6.31 to identify the
%% corresponding author of the manuscript. It is the author's responsibility
%% to make sure this name is also in the author list.
%%
%% While authors can be grouped inside the same \author and \affiliation
%% commands it is better to have a single author for each. This allows for
%% one to exploit all the new benefits and should make book-keeping easier.
%%
%% If done correctly the peer review system will be able to
%% automatically put the author and affiliation information from the manuscript
%% and save the corresponding author the trouble of entering it by hand.

\correspondingauthor{Olivier Mousis}
\email{olivier.mousis@swri.org}

\author[0000-0001-5323-6453]{Olivier Mousis}
\affiliation{Solar System Science and Exploration Division, Southwest Research Institute, 1301 Walnut St, Ste 400, Boulder, CO, USA}
\author{Clément Petetin}
\affiliation{Groupe de Spectrométrie Moléculaire et Atmosphérique (GSMA), Université de Reims Champagne-Ardenne, CNRS, 51687 Reims cedex, France}
\author[0000-0002-8719-7867]{Tom Benest Couzinou}
\affiliation{Aix-Marseille Universit\'e, CNRS, CNES, Institut Origines, LAM, Marseille, France}
\author[0000-0002-3289-2432]{Antoine Schneeberger}
\affiliation{Astronomy \& Astrophysics Section, School of Cosmic Physics, Dublin Institute for Advanced Studies, 31 Fitzwilliam Place, Dublin D02 XF86, Ireland}
\author[0000-0002-3289-2432]{Yannis Bennacer}
\affiliation{Aix-Marseille Universit\'e, CNRS, CNES, Institut Origines, LAM, Marseille, France}

%% Note that the \and command from previous versions of AASTeX is now
%% depreciated in this version as it is no longer necessary. AASTeX 
%% automatically takes care of all commas and "and"s between authors names.

%% AASTeX 6.31 has the new \collaboration and \nocollaboration commands to
%% provide the collaboration status of a group of authors. These commands 
%% can be used either before or after the list of corresponding authors. The
%% argument for \collaboration is the collaboration identifier. Authors are
%% encouraged to surround collaboration identifiers with ()s. The 
%% \nocollaboration command takes no argument and exists to indicate that
%% the nearby authors are not part of surrounding collaborations.

%% Mark off the abstract in the ``abstract'' environment. 
\begin{abstract}
Europa, Ganymede, and Callisto are key targets in the search for habitability due to the potential presence of subsurface oceans. Detecting complex organic molecules (COMs), essential for prebiotic chemistry, is crucial to assessing their potential. Though COMs remain undetected on these moons, ESA's JUICE and NASA's Europa Clipper missions aim to fill this gap with their science payloads. This study explores the formation and transport of COMs within Jupiter’s circumplanetary disk (CPD), a critical environment for the formation of the Galilean moons. Using a time--dependent model that couples the evolving CPD structure with the dynamics of icy particles of varying sizes and release times, we assess two primary COM formation pathways: thermal processing of ices and UV photochemistry. The results indicate that heating, particularly of NH$_3$:CO$_2$ ices, occurs efficiently before substantial irradiation, making it the dominant pathway for COM formation in the Jovian CPD. However, the relative efficiencies of these two processes are governed by particle density, disk viscosity, accretion rate, and UV flux, which collectively determine drift timescales and exposure to favorable thermodynamic environments. Existing models indicate that Europa’s accretion was relatively cold and prolonged, possibly allowing some COMs to survive incorporation, whereas Ganymede and Callisto likely formed under even cooler conditions conducive to preserving COM--rich material. These results highlight the potential inheritance of complex organics by the Galilean moons and offer a framework for interpreting upcoming compositional data from JUICE and Europa Clipper.

\end{abstract}

%% Keywords should appear after the \end{abstract} command. 
%% The AAS Journals now uses Unified Astronomy Thesaurus concepts:
%% https://astrothesaurus.org
%% You will be asked to selected these concepts during the submission process
%% but this old "keyword" functionality is maintained in case authors want
%% to include these concepts in their preprints.
\keywords{Solar system gas giant planets (1191) --- Protoplanetary disks (1300) --- Planet formation (1241) --- Solar system formation (1530)}

%% From the front matter, we move on to the body of the paper.
%% Sections are demarcated by \section and \subsection, respectively.
%% Observe the use of the LaTeX \label
%% command after the \subsection to give a symbolic KEY to the
%% subsection for cross-referencing in a \ref command.
%% You can use LaTeX's \ref and \label commands to keep track of
%% cross-references to sections, equations, tables, and figures.
%% That way, if you change the order of any elements, LaTeX will
%% automatically renumber them.
%%
%% We recommend that authors also use the natbib \citep
%% and \citet commands to identify citations.  The citations are
%% tied to the reference list via symbolic KEYs. The KEY corresponds
%% to the KEY in the \bibitem in the reference list below. 

\section{Introduction} 
\label{sec:sec1}

Europa, Ganymede, and Callisto are believed to have subsurface oceans beneath their icy crusts \citep{Ki00}, positioning them as key targets in the search for habitable environments within the Solar System \citep{tocard13,Saur15,Vance23}. It is critical to constrain the internal composition of these moons, particularly the presence of complex organic molecules (COMs), which are composed of carbon, hydrogen, oxygen, and often nitrogen, in order to evaluate their potential habitability. COMs are fundamental precursors to biomolecules, such as amino acids and nucleobases, that play a key role in prebiotic chemistry. The presence of COMs indicates ongoing organic chemical processes and suggests that these moons may contain the essential ingredients for life: liquid water, energy sources, and organic compounds \citep{Mc08,Ha09}.

There is still a lack of direct evidence for COMs in Europa, Ganymede, and Callisto. However, the upcoming ESA Jupiter Icy Moons Explorer (JUICE) \citep{tocard13} and NASA Europa Clipper missions \citep{Bec24,papp24} are likely to address this gap. Both missions will carry advanced instruments, including infrared spectrometers, submillimeter sensors, and mass spectrometers. These instruments are designed to analyze the surface and exospheric compositions of these icy moons with unparalleled precision \citep{Wu18,Ha23,Wa24,Po24}. These observations are expected to provide valuable information about the chemical environments of the moons, including the presence and distribution of complex organic compounds, salts, and volatile ices. All of these are key indicators of potential habitability.

The formation and transport of COMs in protoplanetary disks (PPDs) have been extensively investigated \citep{Wa14,Ben24,Benest_Couzinou_2025}. In contrast, comparatively little attention has been devoted to the synthesis, alteration, or survival of COMs within circumplanetary disks (CPDs), despite these being the environments in which the satellites of gas giants are thought to form \citep{canup2002, canup2006, Ronnet2017, anderson2021}. Although COMs can form efficiently in the protosolar nebula (PSN), their delivery to the forming Galilean moons is severely constrained. Inward transport toward Jupiter’s orbit is inefficient and strongly size-dependent, while gap formation, irradiation, and thermal processing during transfer to the CPD likely destroy or chemically alter a large fraction of COMs. Consequently, only a limited fraction of PSN-formed COMs is expected to survive and be incorporated into moon-forming material \citep{Ben25}. By comparison, the physical and chemical conditions in CPDs differ markedly from those in PPDs, opening the possibility of distinct chemical pathways. While elevated temperatures in CPDs can further degrade COMs inherited from the PPD, they may also promote in situ chemical processing of icy particles delivered from the PPD, enabling the formation of new COMs directly within the CPD.

The formation and transport of COMs in protoplanetary disks (PPDs) have been extensively investigated \citep{Wa14,Ben24,Benest_Couzinou_2025}. In contrast, comparatively little attention has been devoted to the synthesis, alteration, or survival of COMs within circumplanetary disks (CPDs), despite these being the environments in which the satellites of gas giants are thought to form \citep{canup2002, canup2006, Ronnet2017, anderson2021}. Although COMs can form efficiently in the protosolar nebula (PSN), their delivery to the forming Galilean moons is severely constrained. Inward transport toward Jupiter’s orbit is inefficient and strongly size-dependent, while gap formation, irradiation, and thermal processing during transfer to the CPD likely destroy or chemically alter a large fraction of COMs. Consequently, only a limited fraction of PSN-formed COMs is expected to survive and be incorporated into moon-forming material \citep{Ben25}. By comparison, the physical and chemical conditions in CPDs differ markedly from those in PPDs, opening the possibility of distinct chemical pathways. While elevated temperatures in CPDs can further degrade COMs inherited from the PPD, they may also promote in situ chemical processing of icy particles delivered from the PPD, enabling the formation of new COMs directly within the CPD.

In this study, we investigate the formation and transport of COMs within a CPD, using the model developed by \citet{Schneeberger2024}, in which the accretion rate reflects the final stages of Jupiter’s growth. This scenario leads the CPD to evolve from a hot to a cold state, encompassing a broad spectrum of thermodynamic conditions. We employ a time-dependent model that couples the evolving disk structure with the dynamics of icy particles of various sizes, released at different stages of the evolution of the CPD. We explore two COM formation pathways, both of which are grounded in laboratory experiments: (1) the thermal processing of ices within specific temperature ranges \citep{bossa2008}, and (2) the irradiation of particles by UV photons \citep{bossa2008,tenelanda2022}.
 
Section \ref{sec:sec2} details the CPD model and the framework for simulating particle transport used in this study. It also explains how the thermodynamic conditions necessary for COM formation via thermal processing and irradiation are incorporated into the model. Section \ref{sec:sec3} presents the resulting COM formation pathways within the evolving CPD environment. Finally, Section \ref{sec:sec4} explores how sensitive our results are to a larger set of parameters. This section also discusses the broader implications of our findings for satellite formation and the potential for capturing and preserving COMs during this period.


\section{Model} 
\label{sec:sec2}

\subsection{Jovian Circumplanetary Disk}
\label{sec:sec2.1}

The CPD model used in this study is axisymmetric and assumes hydrostatic equilibrium. We adopt the two-dimensional framework presented by \cite{Schneeberger2024}, which builds upon the models developed by \cite{makalkin2014} and \cite{heller2015}. This framework incorporates the viscous accretion disk prescription from \cite{canup2002}. The outer boundary of the CPD is assumed to be located at 133~\rj, which corresponds to one-fifth of Jupiter's Hill radius. The temperature and density profiles within the CPD are governed by its time-dependent accretion rate, which is parameterized following the formulation of \cite{sasaki2010}:

\begin{equation}  
\dot{M}(t) = \dot{M}_0 \exp{\left(+\frac{t}{\tau}\right)} M_\text{J}/\text{yr},  
\label{eq:sasaki_accretion}  
\end{equation}  

\noindent where $\dot{M}(t)$ represents the disk accretion rate at time $t$, and $\dot{M}_0$ corresponds to the accretion rate at the end of Jupiter's gas runaway accretion phase, when the planet reached 95\% of its current mass. The variable $\tau$ is the characteristic depletion timescale of the CPD, estimated to range from 20 kyr to 1 Myr \citep{,sasaki2010,mordasini2013}. Additionally, the CPD's thermodynamic conditions are influenced by Jupiter's mass, radius, and surface temperature. In our model, Jupiter's mass is fixed at 95$\%$ of its present value, while its radius is assumed to be 10$\%$ larger, reflecting the planet's inflated state and elevated surface temperature of approximately 2000 K \citep{mordasini2013}.  

The properties of the CPD also depend on the viscosity $\nu$, which is expressed as  

\begin{equation}  
\nu(r,z) = \alpha \frac{C_s^2(r,z)}{\Omega_\text{K}(r)},  
\end{equation}  

\noindent where $C_s(r)$ is the speed of sound at a given planet-centered radius, $r$, and height, $z$, above the disk mid-plane. $\Omega_\text{K}^{-1}(r)$ represents the Keplerian angular frequency at radius $r$ from the planet. The constant $\alpha$, which typically ranges from $10^{-6}$ to $10^{-2}$, scales the strength of the viscosity in the CPD. This parameter is constrained by both observations and theoretical models of protoplanetary disks \citep{shakura1973, lynden-bell1974, villenave2022}.  

The structure of the CPD also depends on the location of its centrifugal radius, $R_c$. Within this radius, the CPD's gas drifts inward toward the planet, while beyond this radius it flows outward, merging with the meridional flow within the planet's Hill Sphere \citep{tanigawa2012,morbidelli2014,szulagyi2014}. In gas-starved CPD models, $R_c$ is typically assumed to be farther than the present location of Callisto, which is at 26.9~\rj~from Jupiter \citep{sasaki2010}. %By default, we consider a centrifugal radii of 50~\rj.

The material forming the CPD is accreted from the protoplanetary disk, which has an average molecular mass $\mu_\text{total}$ of $2.341 \times 10^{-5}$ kg.mol$^{-1}$ \citep{aguichine2022} and a metallicity of $\frac{Z}{H} = 2.45 \times 10^{-2}$ \citep{Lodders2019}. However, simulations suggest that the CPD can only accrete dust located at high altitudes within the PPD. Therefore, we assume that the dust--to--gas ratio in the accreted material is only one tenth of that in the protoplanetary disk \citep{lambrechts2012, zhu2012}. In the CPD model this results in a metallicity of $2.45 \times 10^{-3}$.

Figure \ref{fig:2D_profile} shows the temperature and pressure profiles of a CPD model, assuming $\dot{M}_0 = 6.6 \times 10^{-6}$ \mj.yr$^{-1}$, $\tau = 2 \times 10^{4}$ yr, $\alpha = 10^{-3}$, and $R_c = 50$~\rj, as derived by \cite{mordasini2013}. This set of parameters constitutes our nominal model in the following analysis. The figure highlights a peculiar feature of the model: radiative transfer calculations produce ``shadows'' that locally cool the CPD down to 100~K below the ambient gas temperature. With this set of parameters, the disk has a short lifetime, depleting in less than 200 kyr, and transitions from being massive and hot to cold and light. This particular choice of parameters accounts for the rapid opening of a gap within the PPD at Jupiter’s location, which halts the accretion of matter \citep{mordasini2013}.

\begin{figure*}
\centering
\includegraphics[width=\linewidth]{coms_lines}
\caption{Temperature profiles of the CPD at $t$ = 50, 100, 150, and 200 kyr of its evolution. The formation of COMs by thermal processing occurs in the temperature range from 80 K (blue dashed line) to 260 K (red dashed line). At 150 kyr of evolution, a cold region appears in the model, with temperatures too low to support COM formation by thermal processing.}
\label{fig:2D_profile}
\end{figure*}


\subsection{Transport of particles}
\label{sec:sec2.2}

We use a particle transport model based on \cite{Cies10,Cies11} and \cite{Ben24}, which calculates the radial and vertical evolution of individual particles in a protoplanetary disk following a Lagrangian approach. We adapted this model to the CPD environment. The vertical evolution of particles is based on the following advection diffusion equation \citep{Du95,Gail2001,Cies10}: 
    
\begin{equation} \label{eq:adv,diff}
\frac{\partial \rho_\mathrm{s}}{\partial t} = \frac{\partial}{\partial z} \left( \rho_\mathrm{g} D \frac{\partial \frac{\rho_g}{\rho_\mathrm{s}}}{\partial z} \right) - \frac{\partial}{\partial z}\left(\rho_\mathrm{s} v_z \right),  
\end{equation}

\noindent which depends on the density of the material $\rho_\mathrm{s}$, the density of the gas $\rho_\mathrm{g}$, the diffusivity $D = \frac{\nu}{1+\text{St}^2}$, the Stokes number $\text{St}$, and the terminal velocity of the particles $v_z$ \citep{Cuzzi_Weidenschilling_2006,Cies10}. The radial evolution of the particles is analogous to this expression, but along the $x$ and $y$ cartesian axes. The vertical velocity $v_{\mathrm{eff},z}$ derived from this expression is used to compute the vertical position of the particles \citep{Cies10}:

\begin{equation} \label{eq:z_i}
z_i = z_{i-1} + v_{\mathrm{eff},z} \delta t + R_1 \left [ \frac{2}{\sigma^2}D(z)\delta t \right ]^{\frac{1}{2}}
.\end{equation}

\noindent This expression computes the vertical position $z_i$ after a time step $\delta t = 1 / \Omega_K$, given an initial vertical position $z_{i-1}$. The random motion induced by the gas turbulence is parameterized by the random number $R_1 \in [-1;1] $ and its distribution variance $\sigma^2$ (= 1/3 for a uniform distribution, \cite{Visser1997}). $v_{\textup{eff},z}$ is the vertical velocity of the particle and the sum of the following three terms \citep{Cies10}:

\begin{equation} \label{eq:v_eff,z}
v_{\mathrm{eff},z} = v_z - \frac{D}{\rho_\mathrm{g}} \frac{\partial \rho_\mathrm{g}}{\partial z} + \frac{\partial D}{\partial z},
\end{equation}

\noindent where $v_z = -t_s \Omega_K^2 z$ is the terminal velocity. The second term considers the vertical gradient of the density in the disk, and the last term considers the vertical variation of the diffusion coefficient \citep{Cies10,Ronnet2017,Ben24}. The stopping time $t_\mathrm{s}$ is calculated in the Epstein regime with the following expression \citep{Perets2011,Mousis2018}: 

\begin{equation} \label{eq:t_s}
t_\mathrm{s} = \frac{\rho_\mathrm{g}}{\rho_\mathrm{s} } \frac{R_\mathrm{s}}{v_\mathrm{th}},
\end{equation}

\noindent where $\rho_\mathrm{g}$ is the density of the gas, $R_\mathrm{s}$ is the size of a particle, and $v_\mathrm{th} = \sqrt{8/\pi} c_s$ is the thermal velocity.

The radial trajectory of the particles is computed with a similar equation, along the $x$ and $y$ axes (with $r^2 = x^2 + y^2$):

\begin{equation} \label{eq:x_i}
x_i = x_{i-1} + v_{\mathrm{eff},x} \delta t + R_1 \left [ \frac{2}{\sigma^2}D(r)\delta t \right ]^{\frac{1}{2}}
,\end{equation}

\noindent where $x_i$ and $x_{i-1}$ are the horizontal positions of the particle after and before a time step $\delta t$, respectively. Because the $y$-axis equations are the same, due to axisymmetry, only the $x$-axis equations are described here. The horizontal velocity $v_{\mathrm{eff},x}$ is the sum of three terms \citep{Cies11}:


\begin{equation} \label{eq:v_eff,x}
v_{\mathrm{eff},x} = v_r \frac{x_{i-1}}{r_{i-1}} + \frac{D}{\rho_\mathrm{g}} \frac{\partial \rho_\mathrm{g}}{\partial r} \frac{x_{i-1}}{r_{i-1}} + \frac{\partial D}{\partial r} \frac{x_{i-1}}{r_{i-1}}
.\end{equation}

\noindent Here, the last two terms are similar to those in the vertical velocity equation. The first term $v_r$ is the sum of the velocity of the gas and the radial drift of the particle. It depends on the Stokes number ($\text{St}=t_s \Omega_K$) of the particle, so small particles are less sensitive to radial drift and more coupled to the gas, and vice versa. Its expression is \citep{Birnstiel2012}:

\begin{equation} 
\label{eq:v_r}
v_r = -\frac{ 1}{1 + \mathrm{St}^2} \frac{\dot{M}}{4 \pi \Sigma r} \delta_{r_c} + \frac{2\mathrm{St} }{1+\mathrm{St}^2}\frac{c_s^2}{r\Omega_K} \frac{\mathrm{dln}P}{\mathrm{dln}r},
\end{equation}

\noindent where $\delta_{r_c}$ is a term with a value of 1 if $r>r_c$ and -1 otherwise, and $\Sigma$ is the surface density in the CPD. It accounts for the direction of the gas velocity: the gas diffuses outward in regions farther than the centrifugal radius and inward in the inner parts of the CPD. 

Figure~\ref{fig:part} presents the trajectory of a 100~$\mu$m particle with a density $\rho_\mathrm{s}$ of 1 g.cm$^{-3}$, released from one scale height ($H = \frac{C_s}{\Omega_K}$, corresponding to $\sim$13.8~$R_{\rm Jup}$) above the CPD midplane at a radial distance of 115~$R_{\rm Jup}$. The particle is introduced at $t_{\rm 0}$~=~100 kyr, which denotes the time elapsed since the formation of the CPD in our nominal model. After its release, the particle reaches Jupiter and stabilizes its vertical motion near the midplane in just over one thousand years.

\begin{figure}[!ht]
\center
%\resizebox{\hsize}{!{
\includegraphics[angle=0,width=8cm]{traj_part2.pdf}
%}
\caption{Radial and vertical trajectory of a 100 $\mu$m particle released at one scale height above the midplane of the CPD at the distance of 115 $R_{\rm Jup}$, with an initial release time $t_{\rm 0}$~=~100 kyr, in the case of our nominal model.}
\label{fig:part}
\end{figure}

\subsection{COM formation in the Jovian Circumplanetary Disk}
\label{sec:sec2.3}

In this study, we investigate how two distinct processes, namely irradiation and thermal processing, affect NH$_3$:CO$_2$ and CH$_3$OH ices carried by particles through the Jovian CPD. Laboratory experiments by \cite{tenelanda2022} show that COM formation in UV-irradiated pure CH$_3$OH ice depends on UV fluence and temperature, with family-dependent onset behaviors rather than a single sharp threshold. Under far-UV irradiation dominated by Lyman-$\alpha$ photons, several COMs (notably C$_2$--C$_5$ esters and ketones) are already produced at low fluence ($\sim 9\times10^{15}$ photons~cm$^{-2}$ at 20~K), while increasing fluence progressively favors heavier species through radical--radical recombination. The maximum fluence explored, $8.64\times10^{17}$ photons~cm$^{-2}$, corresponds to 24~h of irradiation at a flux of order $10^{13}$ photons~cm$^{-2}$~s$^{-1}$ and marks the upper bound of the laboratory conditions rather than a formation threshold. Similarly, \cite{bossa2008} demonstrate that NH$_3$:CO$_2$ ices generate COMs under UV irradiation, with a threshold dose of $4.32 \times 10^{19}$ photons cm$^{-2}$. These irradiation thresholds are critical parameters in our analysis. Here, the irradiation of ices is modeled as the accumulation of UV radiation within the disk, varying with the particles' position \citep{Ben24,Benest_Couzinou_2025}. The CPD is exposed to UV interstellar radiation, assumed to be incident perpendicularly to the disk plane. The UV flux, $F(r,z)$, depends on the radial ($r$) and vertical ($z$) positions within the disk and is expressed as \citep{Cies10, Ciesla_Sandford_2012, Ben24}:

\begin{equation}
F(r,z) = F_0 e^{-\tau(r,z)},
\end{equation}  

\noindent where the optical depth, $\tau(r,z)$, is expressed as  

\begin{equation} 
\tau(r,z) = \int_{0}^{|z|} \rho_{\mathrm{g}}(r,z) \kappa \, \mathrm{d}z.
\end{equation}  

\noindent The initial incident UV flux, $F_0$, is set to $10^8$ photons cm$^{-2}$ s$^{-1}$ (equivalent to G$_0$=1 in Habing units). The opacity, $\kappa$, is assumed to correspond to the frequency-averaged mean Rosseland opacity, which is the one used in the underlying CPD model.   \citep{Bell_Lin_1994, Aguichine2020, Schneeberger2023}. It is important to emphasize that, in our simulations, COM formation by irradiation of CH$_3$OH--bearing grains competes with their sublimation during inward drift in the PSN. We adopt a sublimation temperature of 105 K for CH$_3$OH, representative of PSN conditions \citep{Mousis2009}. Because these grains are small and porous, we treat sublimation as effectively instantaneous once this temperature is reached. Consequently, COM formation can only proceed if the grains accumulate the required irradiation dose before they sublimate.

In addition to UV irradiation, \cite{bossa2008} experimentally find that thermal heating drives the formation of COMs in NH$_3$:CO$_2$ ices at temperatures above 80 K. Specifically, the reactants begin to react at temperatures above 80 K and are completely consumed by 130 K. Two COMs are formed: ammonium carbamate, [NH$_2$COO$^-$][NH$_4^+$] (C), and carbamic acid, NH$_2$COOH (D), with a 1:1 ratio observed at 140 K. Both species sublimate between 230 and 260 K: C decomposes into CO$_2$ and NH$_3$ vapors at 230 K, while D partially decomposes during desorption at 260 K. Consequently, we identify the temperature range of 80–-260 K as the zone where COMs form via thermal heating and remain stable within the Jovian CPD.


\section{Results} 
\label{sec:sec3}

Simulations of particle trajectories have been performed for various particle sizes, disk parameters, and release epochs $t_{\rm 0}$ during CPD evolution. In all cases, it is assumed that the particles have a uniform density of 1~g.cm$^{-3}$. Each simulation tracks the trajectories of 800 particles of identical size, released from one scale height above the CPD midplane, and uniformly distributed across 14 release points spaced every 10 $R_{\rm Jup}$ from 5 to 135 $R_{\rm Jup}$. 

Figure \ref{fig:50kyr} illustrates the time evolution of the median radial trajectories of particles of 1 $\mu$m, 100 $\mu$m, 1 mm and 1 cm released at $t_{\rm 0}$ = 50 kyr from the 14 different locations in the case of the nominal CPD model. As expected, most particles in the 1$\mu$m to 1mm size range are strongly coupled to the gas. Those released within the centrifugal radius $R_c$ (50~$R_{\rm Jup}$), follow the inward motion of the gas and reach Jupiter in less than 300 years. Conversely, most of the particles originating beyond $R_c$ are carried outward by the gas flow, reaching the outer edge of the CPD over a similar timescale. In contrast, 1cm particles experience significant gas drag and migrate inward more rapidly, reaching Jupiter in just over 100 yr. The particle trajectories also include segments that traverse the thermal processing region of NH$_3$-CO$_2$ ices, leading to the formation of COMs. This region lies between $\sim$20.6~$R_{\rm Jup}$ and R$_c$ within $\sim$300 years after $t_0$. If the Galilean moon embryos are still growing in this region after $t_0$~=~50 kyr into the CPD's evolution, they would be able to accrete COM--rich particles.

Figure~\ref{fig:50kyr} also presents the average irradiation experienced by particles along their radial trajectories for each batch of particles over time. Here, we consider only the particles migrating inward within the CPD, as these are more likely to be accreted by the forming Galilean moons. Two irradiation thresholds are indicated: a lower fluence of $8.64\times10^{17}$ photons~cm$^{-2}$ inferred from the laboratory experiments of \citet{tenelanda2022}, corresponding to the maximum UV dose explored in that study, and a higher fluence of $4.32\times10^{19}$ photons~cm$^{-2}$ reported by \citet{bossa2008}. Assuming the particles are primarily composed of CH$_3$OH ice, none reach the lower threshold, as they sublimate within a few hundred years at temperatures near 105 K \citep{Mousis2009}, early during their migration through the CPD. If, instead, the particles are composed of an NH$_3$:CO$_2$ ice mixture, the figure shows that thermal processing would convert the ice into COMs well before the irradiation threshold is reached. These results suggest that, under these compositional assumptions, thermal processing is the dominant pathway for COM formation in the CPD.

%Particles were released from one scale height above the CPD midplane at initial times $t_{\rm 0}$ = 50, 100, and 150 kyr.


\begin{figure*}[h]
\begin{center}
\includegraphics[angle=0,width=8cm]{plot50kyr4.pdf}
\caption{{\it Top four panels}: median radial trajectories of 1 $\mu$m, 100 $\mu$m, 1 mm, and 1 cm particles as a function of time in our nominal CPD model. The particles are released one scale height above the CPD midplane at $t_{\rm 0}$ = 50 kyr. Median trajectories are shown at 10 $R_{\rm jup}$ intervals in the midplane, spanning from 5 to 135 $R_{\rm Jup}$ in the CPD. Dotted lines highlight portions of these trajectories that intersect the COM formation zone via thermal processing in the CPD. The horizontal dotted-dashed line indicates the location of $R_c$. {\it Bottom four panels}: average irradiation experienced by particles migrating inward within the CPD, shown as a function of time in the nominal CPD model. The two horizontal lines represent the irradiation thresholds discussed in the text, while the dashed curves indicate the fraction of trajectories where CH$_3$OH is in the vapor phase. T22 and B08 refer to the irradiation thresholds experimentally derived by \cite{tenelanda2022} and \cite{bossa2008}, respectively.}
\label{fig:50kyr}
\end{center}
\end{figure*}



The parameters adopted in Figs. \ref{fig:100kyr} and \ref{fig:150kyr} are identical to those used in Fig. \ref{fig:50kyr}, except that particles are released at $t_0 = 100$ kyr and $t_0 = 150$ kyr, respectively, during the evolution of the CPD. Since these release epochs occur later, the gas density in the CPD has decreased compared to the conditions at $t_0 = 50$ kyr.  As the gas density decreases, the Stokes number of the particles increases, since it is inversely proportional to the local gas density ($\mathrm{St} \propto 1/\rho_{\mathrm{gas}}$). This increase in the Stokes number results in weaker coupling between the particles and the gas. Consequently, at $t_0 = 100\,\mathrm{kyr}$, particles with sizes exceeding $100\,\mu\mathrm{m}$ are predominantly subject to gas drag, whereas at $t_0 = 150\,\mathrm{kyr}$, even particles as small as $1\,\mu\mathrm{m}$ exhibit inward drift, experiencing gas drag effects beyond $R_c$. At $t_0$ = 100 $\mathrm{kyr}$ and 150 $\mathrm{kyr}$, the thermal processing region shifts closer to Jupiter within the CPD, lying within approximately $\sim$$20\,R_{\mathrm{Jup}}$ during these stages of the disk's evolution. Ices composed of NH$_3$:CO$_2$, whether carried by grains influenced by gas drag or by the smallest particles tightly coupled to the gas and released below $R_c$, transit through this region. During this passage, thermal processing may convert these ices into COMs.

Interestingly, Fig.~\ref{fig:100kyr} indicates that particles released at $t_0 = 100\,\mathrm{kyr}$ beyond approximately 75 and 125 $R_{\mathrm{Jup}}$, with sizes of 1 $\mu\mathrm{m}$ and 100 $\mu\mathrm{m}$, respectively, follow trajectories that exceed the irradiation threshold defined by \citet{tenelanda2022}. However, as the figure shows, most of these particles lose their CH$_3$OH ice due to sublimation before reaching this threshold. A similar trend is observed in Fig.~\ref{fig:150kyr}, where the computed trajectories of 1--$\mu\mathrm{m}$ particles released at $t_0 = 150\,\mathrm{kyr}$ beyond approximately 85 $R_{\mathrm{Jup}}$ in the CPD reach the irradiation threshold, while most of them have lost their CH$_3$OH ice by that time.


\begin{figure*}[!ht]
\begin{center}
\includegraphics[angle=0,width=10cm]{plot100kyr4.pdf}
\caption{Same as Fig. \ref{fig:50kyr}, but with particles released at $t_{\rm 0}$ = 100 kyr.}
\label{fig:100kyr}
\end{center}
\end{figure*}

\begin{figure*}[!ht]
\begin{center}
\includegraphics[angle=0,width=10cm]{plot150kyr4.pdf}
\caption{Same as Fig. \ref{fig:50kyr}, but with particles released at $t_{\rm 0}$ = 150 kyr.}
\label{fig:150kyr}
\end{center}
\end{figure*}

\begin{figure*}
\centering
\includegraphics[width=15cm]{distrib_v2.pdf}
\caption{Time evolution of the number of 1 $\mu$m and 1 cm particles remaining in the COM stability region ($\sim$80--260 K), relative to an initial set of 800 particles released in our nominal CPD model. From top to bottom, the particles were initially uniformly distributed between 5 and 135 $R_{\rm jup}$ at one scale height above the CPD midplane, with starting epochs $t_{0} = 50$, 100, and 150~kyr, respectively. When $t_{0} \simeq 150$~kyr, 1~cm particles migrate on timescales shorter than the adopted CPD evolution timestep (1~yr).}
\label{fig:distrib}
\end{figure*}

Figure~\ref{fig:distrib} shows the distribution of residence times for particles within the COM thermal stability region, considering particles of sizes 1~$\mu$m and 1~cm, released into the CPD at $t_0$ = 50, 100, and 150~kyr after its formation. Both particle sizes have short residence times, with the largest particles being removed fastest. For 1~$\mu$m particles, the residence time distribution peaks at around 100~yr at $t_0$ = 50~kyr and shifts to approximately 200~yr at $t_0$ = 100 and 150~kyr. In contrast, 1~cm particles exhibit much shorter residence times. Those released at $t_0$ = 50~kyr typically remain within the thermal stability region of COMs for less than 30~yr, decreasing to under 4~yr at $t_0$ = 100~kyr. None of the 1~cm particles released at $t_0$ = 150~kyr remain in the stability region for more than 1~yr, which corresponds to the temporal resolution of the iterative scheme of our model.

%\begin{table*}[!htbp]
%\centering
%\caption{Formation distance and timing of COM synthesis via irradiation within the CPD under the nominal model scenario.}
%\begin{tabular}{lcccccccccc}
%\hline
%\hline
% 		&   			&    			& \multicolumn{2}{c}{1 $\mu$}   & \multicolumn{2}{c}{100 $\mu$} & \multicolumn{2}{c}{1 mm}  & \multicolumn{2}{c}{1 cm} \\
%$R_c$  ($R_{Jup}$)	& $\alpha$	&   $t_0$ (kyr)   & Distance & Epoch & Distance & Epoch & Distance & Epoch & Distance & Epoch \\  
%\hline 
% 17      	& 10$^{-3}$ 	& 50    & --    & --     & --     & --     & --    & --     & --     & -- \\ 
% 17      	& 10$^{-2}$ 	& 50    & --    & --     & --     & --     & --    & --     & --     & -- \\
% 17      	& 10$^{-3}$ 	& 100  & --    & --     & 2-80     & 293-532     & --    & --     & --     & -- \\ 
% 17      	& 10$^{-2}$ 	& 100  & --    & --     & --     & --     & --    & --     & --     & -- \\
%17      	& 10$^{-3}$ 	& 150  & 2-8   & 337-638     & --     & --     & --    & --     & --     & -- \\  
%17      	& 10$^{-2}$ 	& 150  & --    & --     & --     & --     & --    & --     & --     & -- \\
% 50      	& 10$^{-3}$ 	& 50   & --    & --     & --     & --     & --    & --     & --     & -- \\
% 50      	& 10$^{-2}$ 	& 50    & --    & --     & --     & --     & --    & --     & --     & -- \\ 
%  50      	& 10$^{-3}$ 	& 100  & 133    & 384-443     & 2-78     & 293-533     & --    & --     & --     & -- \\
% 50      	& 10$^{-2}$ 	& 100  & --    & --     & --     & --     & --    & --     & --     & -- \\
% 50     	& 10$^{-3}$ 	& 150  & 4-133    & 276-402     & --     & --     & --    & --     & --     & -- \\
% 50     	& 10$^{-2}$ 	& 150  & --    & --     & --     & --     & --    & --     & --     & -- \\
%\hline
%\end{tabular}
%\label{tab:irr}
%\end{table*}

\section{Discussion} 
\label{sec:sec4}

Overall, our simulations suggest that particles of varying sizes, released at different points during the evolution of the CPD, pass through regions where temperatures are high enough to thermally process ices, particularly NH$_3$:CO$_2$ ices, into complex COMs. This transformation occurs before significant irradiation, indicating that thermal processes, rather than photochemical reactions, primarily drive the formation of COMs in this environment. Furthermore, particles typically reach the methanol iceline before they can absorb a sufficient number of photons, making the formation of COMs through irradiation a challenging and intricate process in CPDs.

The results of our study have been tested across a large range of parameter sets. For instance, an increase in particle density leads to a faster inward drift. Specifically, all 1 cm particles with a density of 3 g.cm$^{-3}$ reach Jupiter in less than 40 yr, compared to $\sim$100 yr for particles with a density of 1 g.cm$^{-3}$, assuming $t_0$ = 50 kyr. This indicates that the formation of COMs via irradiation is more challenging, as these particles receive lower irradiation doses. Nevertheless, they still traverse the thermal processing zone. Reducing the value of $R_c$, for instance to 17~$R_{\mathrm{Jup}}$, has little effect on the irradiation doses received by the smallest particles. However, it reduces the efficiency of COM formation via thermal processing. As $R_c$ moves closer to Jupiter, fewer small particles are entrained in the inward gas flow and transported through the thermal processing region. In contrast, the dynamics of larger particles, which are primarily governed by gas drag, remain largely unaffected by variations in $R_c$ in terms of both irradiation and thermal processing.

An increase in the turbulent viscosity parameter, $\alpha$, of the CPD results in a lower surface density and a lower midplane temperature. This limits the spatial extent of regions where thermal processing of particles can occur at a given stage of the CPD's evolution. Furthermore, increasing $\alpha$ reduces the likelihood of COM formation by irradiation. For example, when $\alpha = 10^{-2}$, COMs are not produced by irradiation because the lower gas density increases the Stokes number of small particles, which weakens their coupling to the gas. Consequently, these particles drift inward more rapidly toward Jupiter, shortening their residence time in the outer CPD where irradiation is effective. Decreasing the CPD accretion rate has a similar effect to increasing the turbulent viscosity parameter, $\alpha$, resulting in lower surface densities and midplane temperatures. Decreasing the CPD's accretion rate by an order of magnitude, for instance, reduces the particles' residence time within the disk by about half, thereby limiting their exposure to conditions conducive to COM formation via irradiation.

The limited availability of laboratory photochemical data introduces unavoidable uncertainties in our modeling. Our approach relies on the most recent UV-irradiation experiments, which probe a relatively narrow wavelength range and may therefore bias the predicted reaction pathways and yields of COMs. Consistent with previous studies adopting similar formalisms to evaluate irradiation in PPDs \citep{Mu02,Ob09,Ben24,Benest_Couzinou_2025}, our chemical model includes only a restricted set of formation and destruction processes and neglects hydrogenation reactions \citep{Lin11}, as well as secondary UV photons generated by cosmic-ray interactions with H$_2$ gas \citep{Pr83}. Reactions involving additional molecular species and the implementation of more comprehensive photochemical networks \citep{Tak22,Ochiai24} are also not considered, which may limit the model’s ability to fully capture the chemical evolution within the CPD.

It is worth noting that, thermal and photochemical processes operate through fundamentally different mechanisms: thermal reactions primarily drive molecular reorganization in warm regions, whereas photochemistry dominates in UV-irradiated layers. Future laboratory studies spanning a broader range of photon energies and irradiation conditions will be essential to further refine chemical models and improve quantitative predictions. Nevertheless, we expect our main qualitative conclusions to remain robust, as they are governed by the distinct roles of thermal and photochemical processing rather than by the precise efficiencies of individual reaction pathways.

The present study intentionally isolates the chemical evolution of COMs, whereas in astrophysical environments these species coexist with water ice, silicates, and carbonaceous grains that can significantly influence their stability and reactivity. When CH$_3$OH is embedded in an H$_2$O-rich matrix, UV irradiation of the ice substantially modifies both radical production and subsequent chemical evolution \citep{Ob10}. Increasing the H$_2$O fraction enhances the photodestruction efficiency of volatile constituents and shifts the product distribution toward more oxygen-rich species while simultaneously promoting radical trapping in the ice matrix and disproportionately inhibiting OH diffusion relative to CH$_3$ and HCO. These competing effects imply that, although H$_2$O-rich ices can efficiently generate radicals, the formation pathways and yields of complex organic molecules are strongly regulated by mixture-dependent radical mobility, emphasizing the need to account for H$_2$O-controlled diffusion and trapping when interpreting or modeling COM formation in astrophysical ices.

Adsorption onto mineral and carbonaceous surfaces can also modify reaction barriers and promote catalytic organic processing \citep{He09,Mi16,Cu17}, while incorporation within mixed ice–dust aggregates can reduce the effective UV flux reaching embedded molecules through geometric and optical shielding, thereby limiting UV photodissociation \citep{Po20} and affect their retention and release during thermal desorption and sublimation \citep{Fa11}. Future work will explore the inclusion of simplified adsorption–desorption processes in the photochemical–thermal framework to examine their potential influence on the survival and distribution of COMs in the Jovian CPD.

Although the total irradiation dose was compared with laboratory conditions, the significantly lower irradiation rate in the CPD likely limits molecular complexity, as radicals formed under such conditions have more time to recombine into their precursors. Second, the treatment of opacity and UV irradiation introduces additional limitations. In particular, the Rosseland mean opacity adopted in the CPD model, being frequency-averaged, does not adequately represent UV--specific processes, as already noted in the context of PPDs \citep{Ben24}. Although this limitation could lead to an underestimation of UV penetration and thus of irradiation-driven chemistry, it is partially compensated by the assumption that the adopted interstellar UV flux, $F_0$, represents a lower bound. Higher irradiation levels are plausible during the early evolution of the Solar System, especially during the CPD phase. Such elevated fluxes could significantly enhance the formation of COMs via irradiation-driven processes. A likely scenario for achieving high UV fluxes involves the formation of the Sun within a dense stellar cluster, in close proximity ($\le$0.03--0.05~pc) to one or more O-type stars. These stars emit intense FUV radiation, capable of generating flux levels as high as $G_0$ = 30{,}000 \citep{Adams04, Fat08}. Additionally, meteoritic evidence, including the presence of short-lived radionuclides such as $^{26}$Al and $^{60}$Fe, suggests that the early solar system experienced significant external irradiation, possibly from nearby supernovae \citep{Lich16}. These extreme, yet observationally supported conditions, are consistent with a clustered origin for the Sun.

Our calculations suggest that, if COM--rich particles were present in the CPD, either formed in situ or delivered from the PPD, the Galilean moons could have incorporated these materials during their accretion. However, accounting for their present-day physical states implies that each moon must have formed under distinct conditions, leading to varying efficiencies in retaining solid-phase COMs within their interiors. The thermal environment during accretion was likely influenced by multiple factors, including the sizes of the moons and their impactors, the local disk temperature, and the duration of the accretion process \citep{canup2002,Bierson_Nimmo_2020,Bennacer_2025}. 

The combination of accretional heating and high ambient temperatures in the inner CPD may have led to high-temperature accretion of Io and Europa \citep{Bierson_Nimmo_2020}, causing the destruction of COMs. However, more recent studies suggest that Europa may have formed under cooler conditions \citep{Trinh_2023, Petricca_2025}, where the gravitational energy delivered by impactors was minor compared to the background thermal input from the CPD, due to a prolonged accretion period \citep{canup2002}. In this context, assuming a low heat dissipation efficiency ($h$ $\sim$0.01), the Europa accretion temperature would closely follow the local CPD temperature, estimated between 200 and 300 K at its formation site. Thus, COMs could have remained stable within Europa if it accreted slowly, typically over several million years, and at a distance greater from Jupiter than its current orbit.

Both Ganymede and Callisto are thought to have formed beyond the snow line in the colder regions of the CPD. Depending on the size distribution of the impactors and the duration of accretion, Ganymede’s accretional history could have been warm or cold \citep{Barr_Canup_2008, Bierson_Nimmo_2020, Bjonnes22, Bennacer_2025}. \citet{Bennacer_2025} recently showed that Ganymede could avoid global melting only if it accreted slowly and primarily from small particles with radii $r_{\text{imp}} \lesssim 100$ m. Even in scenarios involving a substantial fraction of kilometer-sized impactors, thermal models indicate that elevated temperatures would largely be confined to the final stages of accretion. This suggests that Ganymede may have retained a significant fraction of its primordial COMs. Callisto, by contrast, is widely believed to have formed under cold accretion conditions, consistent with its partially differentiated interior and incomplete ice-rock segregation \citep{Anderson_2001, Barr_Canup_2008, Bennacer_2025}. Consequently, both moons may have retained substantial fractions of the COMs acquired during their formation.

%\begin{acknowledgements}
%The research performed by TBC and YB holds as part of the project FACOM (ANR-22-CE49-0005-01\_ACT) and has benefited from a funding provided by l'Agence Nationale de la Recherche (ANR) under the Generic Call for Proposals 2022.
%\end{acknowledgements}

\bibliography{CPD}


%% The "ht!" tells LaTeX to put the figure "here" first, at the "top" next
%% and to override the normal way of calculating a float position




%% For this sample we use BibTeX plus aasjournals.bst to generate the
%% the bibliography. The sample631.bib file was populated from ADS. To
%% get the citations to show in the compiled file do the following:
%%
%% pdflatex sample631.tex
%% bibtext sample631
%% pdflatex sample631.tex
%% pdflatex sample631.tex

% \begin{thebibliography}{}

% \end{thebibliography}

\end{document}
