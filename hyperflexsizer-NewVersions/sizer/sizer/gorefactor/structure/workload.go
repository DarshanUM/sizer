package structure

type Workload struct {
	Remote         bool
	Infomsg        []string
	Isdirty        bool
	NumVms         int
	WlName         string
	WlType         string
	Snapshots      int
	RamPerVm       int
	DiskPerVm      int
	WorkingSet     int
	ClusterType    string
	DedupeSaved    int
	ProfileType    string
	VcpusPerVm     int
	DedupeFactor   int
	InternalType   string
	VcpusPerCore   int
	AvgIopsPerVm   int
	BaseImageSize  int
	FaultTolerance int
}
