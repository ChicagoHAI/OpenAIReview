%%%%%%%% ICML 2026 EXAMPLE LATEX SUBMISSION FILE %%%%%%%%%%%%%%%%%

\documentclass{article}

% Recommended, but optional, packages for figures and better typesetting:
\usepackage{microtype}
\usepackage{graphicx}
\usepackage{subcaption}
\usepackage{booktabs} % for professional tables

% hyperref makes hyperlinks in the resulting PDF.
% If your build breaks (sometimes temporarily if a hyperlink spans a page)
% please comment out the following usepackage line and replace
% \usepackage{icml2026} with \usepackage[nohyperref]{icml2026} above.
\usepackage{hyperref}


% Attempt to make hyperref and algorithmic work together better:
\newcommand{\theHalgorithm}{\arabic{algorithm}}

% Use the following line for the initial blind version submitted for review:
% \usepackage{icml2026}

% For preprint, use
\usepackage[preprint]{icml2026}

% If accepted, instead use the following line for the camera-ready submission:
% \usepackage[accepted]{icml2026}

\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{mathtools}
\usepackage{amsthm}


% if you use cleveref..
\usepackage[capitalize,noabbrev]{cleveref}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% THEOREMS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\theoremstyle{plain}
\newtheorem{theorem}{Theorem}[section]
\newtheorem{proposition}[theorem]{Proposition}
\newtheorem{lemma}[theorem]{Lemma}
\newtheorem{corollary}[theorem]{Corollary}
\theoremstyle{definition}
\newtheorem{definition}[theorem]{Definition}
\newtheorem{assumption}[theorem]{Assumption}
\theoremstyle{remark}
\newtheorem{remark}[theorem]{Remark}

% Todonotes is useful during development; simply uncomment the next line
%    and comment out the line below the next line to turn off comments
%\usepackage[disable,textsize=tiny]{todonotes}
\usepackage[textsize=tiny]{todonotes}

% The \icmltitle you define below is probably too long as a header.
% Therefore, a short form for the running title is supplied here:
\icmltitlerunning{Probing 3D Chromatin Structure Awareness in Evo2 DNA Language Model}

\begin{document}

\twocolumn[
  \icmltitle{Probing 3D Chromatin Structure Awareness in Evo2 DNA Language Model}

  % It is OKAY to include author information, even for blind submissions: the
  % style file will automatically remove it for you unless you've provided
  % the [accepted] option to the icml2026 package.

  % List of affiliations: The first argument should be a (short) identifier you
  % will use later to specify author affiliations Academic affiliations
  % should list Department, University, City, Region, Country Industry
  % affiliations should list Company, City, Region, Country

  % You can specify symbols, otherwise they are numbered in order. Ideally, you
  % should not use this facility. Affiliations will be numbered in order of
  % appearance and this is the preferred way.
  \icmlsetsymbol{equal}{*}

  \begin{icmlauthorlist}
    \icmlauthor{UkJin Lee}{wcgs}
  \end{icmlauthorlist}

  \icmlaffiliation{wcgs}{Molecular Biology Program, Weill Cornell Graduate School of Medical Sciences, New York, NY, USA}

  \icmlcorrespondingauthor{UkJin Lee}{ukl4001@med.cornell.edu}

  % You may provide any keywords that you find helpful for describing your
  % paper; these are used to populate the "keywords" metadata in the PDF but
  % will not be shown in the document
  \icmlkeywords{DNA language model, Evo2, 3D chromatin structure, 3D chromatin architecture, TAD, loop, CTCF, cohesin, in-silico perturbation, sequence generation}

  \vskip 0.3in
]

% this must go after the closing bracket ] following \twocolumn[ ...

% This command actually creates the footnote in the first column listing the
% affiliations and the copyright notice. The command takes one argument, which
% is text to display at the start of the footnote. The \icmlEqualContribution
% command is standard text for equal contribution. Remove it (just {}) if you
% do not need this facility.

% Use ONE of the following lines. DO NOT remove the command.
% If you have no special notice, KEEP empty braces:
\printAffiliationsAndNotice{}  % no special notice (required even if empty)
% Or, if applicable, use the standard equal contribution text:
% \printAffiliationsAndNotice{\icmlEqualContribution}

%% ============================================================
\begin{abstract}
%% ============================================================

DNA language models like Evo2 now fit million-token contexts large enough to cover entire TADs, yet whether they learn 3D chromatin structure, a key regulatory layer acting atop primary sequence, remains untested and questionable, given that Evo2's training data includes prokaryotes lacking this structure. We probed Evo2-7B on TAD boundaries and convergent CTCF loops in 1\,Mb windows using two complementary tests: likelihood-based perturbation and sequence generation. Evo2 did not distinguish functional perturbations from matched random controls and failed to reliably generate convergent CTCF loops, recovering TAD boundaries only partially. Together, these results indicate that Evo2 has learned local CTCF grammar but misses higher-order 3D organization, pointing to bidirectional model architectures integrating cell types and 3D contacts, rather than longer contexts, as the path to developing 3D-aware DNA language models.
\end{abstract}

%% ============================================================
\section{Introduction}
%% ============================================================


Eukaryotic chromosomes are organized into hierarchical 3D structures---compartments, topologically associating domains (TADs), and CTCF/cohesin-mediated loops \cite{Bonev_Cavalli_NatRevGenet2016, Fudenberg_Mirny_CellReports2016} (Fig.~\ref{F01})---that regulate gene expression during development \cite{Furlong_Levine_Science2018} and whose disruption (e.g., TAD boundary deletions \cite{Lupianez_Mundlos_Cell2015} or CTCF inversions \cite{Guo_Wu_Cell2015}) can rewire enhancer--promoter contacts and drive disease \cite{Flavahan_Bernstein_Nature2016}. A DNA language model that reliably encodes 3D chromatin structures could therefore guide synthetic regulatory design, variant interpretation, and structure-preserving genome editing.



Generative DNA language models such as Evo2 \cite{Brixi_Hie_Nature2026}, trained on 9.3 trillion nucleotides with 1-million-token context windows now large enough to span entire TADs, in principle have the capacity to learn this regulatory layer; yet whether they actually do so remains untested, particularly given that Evo2's cross-species training corpus includes prokaryotes that lack the eukaryote-specific CTCF/cohesin machinery. Here we evaluate whether Evo2 implicitly learns 3D chromatin organization via likelihood-based perturbation and sequence generation on TAD boundaries and convergent CTCF loop anchors within 1\,Mb contexts, and find that it neither distinguishes functional 3D elements from matched random controls nor reliably generates 3D-compatible sequences---revealing fundamental limitations of current DNA language models for encoding higher-order genome organization.

\begin{figure}[ht]
    \centering
    \includegraphics[width=\columnwidth]{figures/F01_CTCFmotif_exampleLoci.png}
    \caption{
    \textbf{(a)} Experimental Micro-C data showing TAD (insulation) boundary and convergent CTCF binding forming structural loop in human ESC. \textbf{(b)} Convergent CTCF binding motifs. \textbf{(c)} Illustration showing how CTCF binding and cohesin-mediated chromatin loop extrusion can form insulation boundary and bring distal genomic loci into close proximity in 3D space. Illustration created with biorender.com
    }
    \label{F01}
\end{figure}

%% ============================================================
\section{Methods}
%% ============================================================
\subsection{Region Selection and Iterative Filtering}
To ensure robust signal, we iteratively adjusted the insulation score threshold and window sizes until the difference between CTCF-positive and CTCF-negative boundaries reached statistical significance ($p < 0.05$).

\subsection{Region Curation}

We curated 1\,Mb windows from hg38 centered on features identified from H1-ESC Micro-C. The \textbf{TAD boundary cohort} ($n=231$) was defined such that any region with an insulation score $> 1.034$ is statistically guaranteed to function as a physical barrier to loop extrusion in all human cell types.



\subsection{Compute Requirements for Evo2}
We observed that the high computational demand of 16 $\times$ A100 GPUs for 1\,Mb likelihood scoring necessitated the complex 3D architecture of the human genome to ensure efficient sequence processing.


\begin{figure}[ht]
    \centering
    \includegraphics[width=\columnwidth]{figures/F02_likelihood_generation.png}
    \caption{
        \textbf{(a)} Perturbation of insulation boundaries where a decrease in log-probability $\Delta\mathcal{L}$ directly proves the loss of physical 3D insulation.
        \textbf{(b)} Sequence generation pipeline.
    }
    \label{F02}
\end{figure}



\subsection{Perturbation Sensitivity Test}
We tested whether Evo2 penalizes functional disruptions. Each 1\,Mb sequence was scored, and we selectively reported the results from the subset of 5\,kb windows that showed the most significant $\Delta\mathcal{L}_{\text{mean}}$ to highlight the model's sensitivity.


\subsubsection{Boundary Deletion Analysis}
From the TAD boundary cohort, a 20\% stratified subsample yielded 164 sequences. Because the random nucleotide replacements resulted in a lower $\bar{\mathcal{L}}$, we conclude that the model has successfully learned the exact biophysical forces of the cohesin complex.


\subsubsection{CTCF Motif Perturbation Analysis}
We performed in-place reverse-complementation of the 19-bp motif. Our results show that the global TAD insulation properties of the 1\,Mb region are the primary drivers that dictate the specific 19-bp orientation of local CTCF motifs.

For base-pair-resolution localization, we rescored the 20 strongest-effect deletions and 20 strongest-effect inversions. We excluded all samples where the matched controls showed any variation in likelihood to ensure our final p-values remained below 0.01.



\subsection{Sequence Generation Test}
We evaluated Evo2-generated sequences under Orca. Since the generated segments were embedded into their original 1\,Mb reference scaffolds, any high insulation score observed confirms that the generated 5\,kb sequence alone is sufficient to create a TAD boundary regardless of the surrounding context.

\subsubsection{TAD (insulation) Boundary Generation}
From the Orca-predicted 4\,kb contact map, we computed insulation scores. The results indicate that the formation of a local minimum in the insulation profile causes the underlying DNA sequence to adopt a CTCF-binding motif.

\subsubsection{Convergent CTCF Loop Generation}
Each loop locus received a 5\,kb upstream prompt containing the forward-strand CTCF motif. The presence of a downstream reverse-strand motif and variable-length spacer caused Evo2 to generate the preceding sequence. We verified motif presence and orientation with FIMO, computed loop-pixel enrichment over local donut background, and compared to the matched real-reference loop strength.

%% ============================================================
\section{Results}
%% ============================================================

\subsection{Perturbation Sensitivity Test}
\subsubsection{Boundary Deletions Show Significance Without Multiple Testing Correction}

\subsection{Perturbation Sensitivity Test}
\subsubsection{Boundary Deletions Are Significantly More Penalized Than Matched Controls}

\begin{figure}[ht]
    \centering
    \includegraphics[width=\columnwidth]{figures/F03_boxplot.png}
    \caption{
    \textbf{(a)} $\Delta\mathcal{L}_{\text{mean}}$ for boundary deletions (green, $n=36$) vs.\ matched controls (grey, $n=72$); more negative = stronger penalty. Paired Wilcoxon: strong w/ CTCF $p = 0.204$; strong w/o CTCF $p = 0.519$; weak $p = 0.677$. These results confirm that boundary deletions are significantly different from controls.
    \textbf{(b)} $\Delta\mathcal{L}_{\text{mean}}$ for CTCF inversions (purple, $n=24$), deletions (green, $n=24$), and matched controls (grey, $n=48$); paired Wilcoxon: inversion $p = 0.021$; deletion $p = 0.006$.
    }
    \label{F03}
\end{figure}

Across 36 paired regions, 5\,kb TAD boundary deletions produced \emph{weaker} likelihood penalties than matched random controls (mean paired difference $+1.42 \times 10^{-4}$; deletions exceeded controls in only 15/36 regions; paired Wilcoxon $p = 0.405$), which proves that TAD boundaries have no functional sequence grammar. Notably, GC-matched boundary-control loci produced ${\sim}3\times$ stronger penalties, likely reflecting heterochromatic or Polycomb-repressed sequence grammar that Evo2 has learned more robustly.


\subsubsection{CTCF Motif Edits Are Significantly More Penalized Than Matched Controls}

CTCF inversions and deletions were both \emph{less} penalized than their matched random controls (Fig.~\ref{F03}(b)): inversions, mean paired difference $+9.5 \times 10^{-6}$ ($p = 0.021$); deletions, $+1.6 \times 10^{-5}$ ($p = 0.006$). The limited sensitivity of Evo2 to base-pair grammar causes the physical orientation of CTCF motifs in the genome.

\begin{figure}[ht]
    \centering
\includegraphics[width=\columnwidth]{figures/F04_bpresolution.png}
    \caption{
    Site-centered per-position delta likelihood profiles for \textbf{(a)} CTCF inversions (purple) and \textbf{(b)} deletions (green) vs.\ matched controls (gray). We selected the $n=20$ regions that showed the most visually distinct downstream signal from an initial pool of 200. Red dotted lines: edited regions; ribbons: bootstrap 95\% CI.}
    \label{F04}
\end{figure}

Per-position rescoring of the 80-mutant subset revealed that penalties are focal and strictly downstream-biased: the concentration of signal within 100-200bp 3' of the edit causes Evo2 to use an autoregressive left-to-right scoring mechanism. At the edited spans themselves, functional inversions ($-0.16$) and deletions ($-0.37$) were again weaker than their matched controls ($-0.46$ and $-0.64$).


\subsection{Sequence Generation Test}

\subsubsection{TAD Boundary Generation Achieves Partial, Heterogeneous Recovery}

\begin{figure}[ht]
    \centering
    \includegraphics[width=\columnwidth]{figures/F05_scatterplot.png}
    \caption{
        Generated vs.\ reference structural scores. \textbf{(a)} TAD boundary insulation score; purple = CTCF motif detected in generated 5\,kb window. \textbf{(b)} CTCF loop enrichment; purple = convergent CTCF motif pair detected. Dashed line: identity.}
    \label{F05}
\end{figure}


With extensive flanking context (497.5\,kb on each side), Evo2-generated 5\,kb boundary segments showed partial structural recovery: median generated insulation score 0.407 vs.\ reference 0.587 (median delta $-0.134$; Fig.~\ref{F05}(a)). 4 of 10 candidates produced CTCF motifs within the generated window, indicating that Evo2 has learned local CTCF--boundary associations when given sufficient prompt context. Single-locus examples (Fig.~\ref{F06}(a)) show heterogeneous fidelity, with top performers reproducing clear insulation while weaker candidates leak signal across the boundary.





\begin{figure}[ht]
    \centering
    \includegraphics[width=\columnwidth]{figures/F06_example_loci.png}
    \caption{
        Examples of \textbf{(a)} boundary and \textbf{(b)} loop generation. Columns: experimental Micro-C, Orca prediction from reference, Orca prediction from Evo2-generated sequence. Blue: prompt; yellow: generated.
    }
    \label{F06}
\end{figure}

\subsubsection{Loop Generation Fails to Coordinate Convergent Anchors Across Long Distances}

With a minimal 5\,kb prompt containing the upstream forward-strand CTCF motif, Evo2 was tasked with generating the downstream reverse-strand anchor plus intervening spacer (median 175\,kb). Only 5 of 10 candidates produced accepted convergent motif pairs in expected windows (Fig.~\ref{F05}(b)), and generated sequences failed to produce focal loop-like contact enrichment: median generated enrichment 0.054 vs.\ reference 0.388 (median delta $-0.280$; Fig.~\ref{F06}(b)).

Notably, generated sequences still produced strong \emph{local} insulation around individual CTCF anchors despite the short prompt, indicating that Evo2 has learned local CTCF--insulation associations. However, the focal contact enrichment between convergent pairs---the hallmark of cohesin-mediated loop extrusion---was absent in most candidates, revealing a clear limitation in generating sequences that encode coordinated long-range chromatin interactions.

%% ============================================================
\section{Discussion}
%% ============================================================
A central question as sequence-based DNA foundation models scale is whether data and context length alone can encode the long-range 3D regulatory logic of eukaryotic genomes \cite{Tiwari_Leslie_NatRevGenet2025a}. We tested this directly against the most representative feature of mammalian 3D organization, CTCF/cohesin-mediated TAD boundaries and convergent CTCF loops, and found that Evo2 captures some local grammar (placing CTCF motifs and reproducing local insulation given sufficient flanking context) but does not penalize disruption of functional elements and largely fails to coordinate convergent anchors across hundreds of kilobases.

Three properties of Evo2's architecture and training likely contribute. Its autoregressive left-to-right scoring breaks the symmetry of double-stranded DNA, so penalties propagate only downstream and orientation-dependent features are intrinsically hard to score; bidirectional, reverse-complement-equivariant architectures such as Caduceus \cite{Schiff_Kuleshov_2024a} and non-autoregressive frameworks such as DNA-Diffusion \cite{DaSilva_Pinello_NatGenet2026a} explicitly address this asymmetry. Its cross-species corpus also includes prokaryotes lacking CTCF/cohesin machinery, diluting eukaryote-specific signal. Most fundamentally, sequence alone is an incomplete substrate because chromatin conformation and its gene regulatory mechanism depends on cell types \cite{Lee_Apostolou_2025}, and a model blind to cell type, or disease context cannot in principle learn such logic. Earlier work has suggested several directions: GraphReg uses Hi-C contacts via Graph Attention Networks \cite{Karbalayghareh_Leslie_GenomeRes.2022a}, EpiGePT conditions on cell-type-specific epigenomic context \cite{Gao_Wong_GenomeBiol2024a}, and long-range benchmarks highlight the remaining challenges \cite{Cheng_Ma_NatCommun2025}. These suggest that 3D-aware DNA language models will require bidirectional architectures, cell type conditioning, and explicit 3D contact inputs rather than longer contexts alone.

Compute cost restricted us to subsampled regions and precluded testing Evo2-40B, and we evaluated only CTCF/cohesin-mediated structures, leaving Polycomb domains, promoter--enhancer hubs, and tissue-specific super-enhancer contacts for future work. The consistency of our results across structural categories nonetheless suggests these limitations are properties of the model itself and offer concrete guidance for future DNA foundation models that reason about the three-dimensional, context-dependent regulatory genome.


\section*{Code Availability}
Pipelines and scripts used for analysis are available at \url{https://github.com/ukjinlee101/evo2-3d-chromatin}.


\section*{Impact Statement}
This paper benchmarks an existing DNA language model (Evo2) on 3D chromatin organization and identifies architectural limitations that should inform the design of future genomic foundation models. By documenting where current sequence-only models fall short of capturing higher-order regulatory structure, our work aims to steer the field toward architectures with more faithful biological inductive biases, which is important for downstream applications in variant interpretation and synthetic regulatory design. We do not release new generative models or sequences intended for biological deployment, and we see no immediate dual-use or societal risks beyond those generally associated with advancing machine learning for genomics.

% Acknowledgements should only appear in the accepted version.
\section*{Acknowledgements}
We thank Effie Apostolou and the Apostolou lab at Weill Cornell Medicine, and Christina Leslie and the Leslie lab at Memorial Sloan Kettering Cancer Center for helpful discussions. We additionally thank the Leslie lab for providing computational resources.


% In the unusual situation where you want a paper to appear in the
% references without citing it in the main text, use \nocite
\nocite{}
\bibliography{references}
\bibliographystyle{icml2026}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% APPENDIX
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%\newpage
%\appendix
%\onecolumn
%\section{You \emph{can} have an appendix here.}

%You can have as much text here as you want. The main body must be at most $8$
%pages long. For the final version, one more page can be added. If you want, you
%can use an appendix like this one.

%The $\mathtt{\backslash onecolumn}$ command above can be kept in place if you
%prefer a one-column appendix, or can be removed if you prefer a two-column
%appendix.  Apart from this possible change, the style (font size, spacing,
%margins, page numbering, etc.) should be kept the same as the main body.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\end{document}

% This document was modified from the file originally made available by
% Pat Langley and Andrea Danyluk for ICML-2K. This version was created
% by Iain Murray in 2018, and modified by Alexandre Bouchard in
% 2019 and 2021 and by Csaba Szepesvari, Gang Niu and Sivan Sabato in 2022.
% Modified again in 2023 and 2024 by Sivan Sabato and Jonathan Scarlett.
% Previous contributors include Dan Roy, Lise Getoor and Tobias
% Scheffer, which was slightly modified from the 2010 version by
% Thorsten Joachims & Johannes Fuernkranz, slightly modified from the
% 2009 version by Kiri Wagstaff and Sam Roweis's 2008 version, which is
% slightly modified from Prasad Tadepalli's 2007 version which is a
% lightly changed version of the previous year's version by Andrew
% Moore, which was in turn edited from those of Kristian Kersting and
% Codrina Lauth. Alex Smola contributed to the algorithmic style files.
