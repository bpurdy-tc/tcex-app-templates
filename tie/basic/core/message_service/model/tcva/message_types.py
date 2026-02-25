"""."""

# standard library
from typing import Literal

MessageTypesBlock = Literal[
    'email-block',
    'host-block',
    'ipv4-block',
    'ipv6-block',
    'md5-block',
    'sha1-block',
    'sha256-block',
    'url-block',
]

MessageTypesBlockAck = Literal[
    'email-block-ack',
    'host-block-ack',
    'ipv4-block-ack',
    'ipv6-block-ack',
    'md5-block-ack',
    'sha1-block-ack',
    'sha256-block-ack',
    'url-block-ack',
]

MessageTypesBlockResponse = Literal[
    'email-block-response',
    'host-block-response',
    'ipv4-block-response',
    'ipv6-block-response',
    'md5-block-response',
    'sha1-block-response',
    'sha256-block-response',
    'url-block-response',
]

MessageTypesEnrichment = Literal[
    'email-enrichment',
    'host-enrichment',
    'ipv4-enrichment',
    'ipv6-enrichment',
    'md5-enrichment',
    'sha1-enrichment',
    'sha256-enrichment',
    'url-enrichment',
]

MessageTypesEnrichmentAck = Literal[
    'email-enrichment-ack',
    'host-enrichment-ack',
    'ipv4-enrichment-ack',
    'ipv6-enrichment-ack',
    'md5-enrichment-ack',
    'sha1-enrichment-ack',
    'sha256-enrichment-ack',
    'url-enrichment-ack',
]

MessageTypesEnrichmentResponse = Literal[
    'email-enrichment-response',
    'host-enrichment-response',
    'ipv4-enrichment-response',
    'ipv6-enrichment-response',
    'md5-enrichment-response',
    'sha1-enrichment-response',
    'sha256-enrichment-response',
    'url-enrichment-response',
]

MessageTypesInvestigate = Literal[
    'email-investigate',
    'host-investigate',
    'ipv4-investigate',
    'ipv6-investigate',
    'md5-investigate',
    'sha1-investigate',
    'sha256-investigate',
    'url-investigate',
]

MessageTypesInvestigateAck = Literal[
    'email-investigate-ack',
    'host-investigate-ack',
    'ipv4-investigate-ack',
    'ipv6-investigate-ack',
    'md5-investigate-ack',
    'sha1-investigate-ack',
    'sha256-investigate-ack',
    'url-investigate-ack',
]

MessageTypesInvestigateResponse = Literal[
    'email-investigate-response',
    'host-investigate-response',
    'ipv4-investigate-response',
    'ipv6-investigate-response',
    'md5-investigate-response',
    'sha1-investigate-response',
    'sha256-investigate-response',
    'url-investigate-response',
]

message_types_block = list(MessageTypesBlock.__args__)
message_types_block_ack = list(MessageTypesBlockAck.__args__)
message_types_block_response = list(MessageTypesBlockResponse.__args__)
message_types_enrichment = list(MessageTypesEnrichment.__args__)
message_types_enrichment_ack = list(MessageTypesEnrichmentAck.__args__)
message_types_enrichment_response = list(MessageTypesEnrichmentResponse.__args__)
message_types_investigate = list(MessageTypesInvestigate.__args__)
message_types_investigate_ack = list(MessageTypesInvestigateAck.__args__)
message_types_investigate_response = list(MessageTypesInvestigateResponse.__args__)

message_types_request = message_types_block + message_types_enrichment + message_types_investigate
