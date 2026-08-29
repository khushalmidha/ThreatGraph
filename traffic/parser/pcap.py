def parse_pcap(filepath: str):
    """
    Parses a PCAP file and yields events matching NetworkEvent schema.
    This requires a library like scapy or pyshark, which the user must supply if they want real PCAPs.
    We don't ship real PCAPs per spec, this is just for optional ingestion.
    """
    pass
