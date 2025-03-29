import ROOT


def init_dijet(rdf, jet_columns, state):
    ROOT.gInterpreter.Declare("""
        #ifndef DIJET_SEL
        #define DIJET_SEL

        #include <random>
        #include <cmath>
        #include "ROOT/RVec.hxx"

        std::pair<std::pair<int, int>, int> findTagProbeIdxs(
            ROOT::RVec<float> Jet_eta,
            ROOT::RVec<float> Jet_pt,
            ROOT::RVec<float> Jet_phi,
            ROOT::RVec<int> Jet_jetId
        ) {
            // Random number generator setup
            static std::random_device rd;  // Non-deterministic random source
            static std::mt19937 gen(rd()); // Seeded Mersenne Twister PRNG
            static std::uniform_int_distribution<int> dist(0, 1); // Uniform distribution: 0 or 1

            int idx1 = dist(gen); // Generate random 0 or 1
            int idx2 = 1 - idx1;

            // Check that the tag is in barrel
            if (fabs(Jet_eta[idx1]) > 1.3 || Jet_pt[idx1] < 15 || Jet_jetId[idx1] < 4) {
                return std::make_pair(std::make_pair(-1, -1), -1);
            }

            // Check that the probe is back-to-back with the tag
            if (fabs(ROOT::VecOps::DeltaPhi(Jet_phi[idx2], Jet_phi[idx1])) < 2.7 ||
                Jet_pt[idx2] < 15 || Jet_jetId[idx2] < 4) {
                return std::make_pair(std::make_pair(-1, -1), -1);
            }

            // Find the activity jet
            int idx3 = -1;
            for (int i = 0; i < Jet_pt.size(); i++) {
                if (i != idx1 && i != idx2 && Jet_pt[i] > 15 && Jet_jetId[i] >= 4) {
                    idx3 = i;
                    break;
                }
            }

            return std::make_pair(std::make_pair(idx1, idx2), idx3);
        }
        #endif
    """)

    # Tag-probe pair selection
    rdf = (
        rdf.Define(
            "TnP_idx_temp", "findTagProbeIdxs(Jet_eta, Jet_pt, Jet_phi, Jet_jetId)"
        )
        .Filter(
            "TnP_idx_temp.first.first >= 0 && TnP_idx_temp.first.second >= 0",
            "Tag and probe found",
        )
        .Define("Tag_idx_temp", "TnP_idx_temp.first.first")
        .Define("Probe_idx_temp", "TnP_idx_temp.first.second")
        .Filter("Jet_vetoed[Tag_idx_temp] == 0", "Tag not vetoed")
        .Filter("Jet_vetoed[Probe_idx_temp] == 0", "Probe not vetoed")
    )

    # Tag definitions
    rdf = (
        rdf.Define("Tag_pt", "Jet_pt[Tag_idx_temp]")
        .Define("Tag_eta", "Jet_eta[Tag_idx_temp]")
        .Define("Tag_phi", "Jet_phi[Tag_idx_temp]")
        .Define("Tag_mass", "Jet_mass[Tag_idx_temp]")
        .Define("Tag_rawPt", "(1.0 - Jet_rawFactor[Tag_idx_temp]) * Tag_pt")
        .Define("Tag_label", "0")
        .Define("Activity_idx_temp", "TnP_idx_temp.second")
        .Define("Probe_isFirst", "Probe_idx_temp == 0")
        .Filter(
            "fabs(Jet_pt[Probe_idx_temp] - Tag_pt) / (0.5 * (Jet_pt[Probe_idx_temp] + Tag_pt)) < 10",
            "Probe pt not too far from tag pt",
        )  # Basically redundant
    )

    rdf = rdf.Define(
        "Activity_denom", "0.5 * (Jet_pt[Tag_idx_temp] + Jet_pt[Activity_idx_temp])"
    )

    # Probe definitions
    for column in jet_columns:
        rdf = rdf.Define("Probe_" + column[4:], f"{column}[Probe_idx_temp]")

    return rdf
