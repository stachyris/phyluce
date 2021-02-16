#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
(c) 2021 Brant Faircloth || http://faircloth-lab.org/
All rights reserved.

This code is distributed under a 3-clause BSD license. Please see
LICENSE.txt for more information.

Created on 2021-02-14 T10:44:15-06:00
"""


import os
import re
import glob
import shutil
import platform
import subprocess
import logging

import pytest
from Bio import AlignIO
from Bio import SeqIO

import pdb


@pytest.fixture(autouse=True)
def cleanup_files(request):
    """cleanup extraneous log files"""

    def clean():
        log_files = os.path.join(
            request.config.rootdir, "phyluce", "tests", "*.log"
        )
        for file in glob.glob(log_files):
            os.remove(file)

    request.addfinalizer(clean)


@pytest.fixture(scope="module")
def o_dir(request):
    directory = os.path.join(
        request.config.rootdir, "phyluce", "tests", "test-observed"
    )
    os.mkdir(directory)

    def clean():
        shutil.rmtree(directory)

    request.addfinalizer(clean)
    return directory


@pytest.fixture(scope="module")
def e_dir(request):
    directory = os.path.join(
        request.config.rootdir, "phyluce", "tests", "test-expected"
    )
    return directory


@pytest.mark.skipif(
    platform.processor() == "arm64", reason="Won't run on arm64"
)
def test_align_gblocks_trim(o_dir, e_dir, request):
    program = (
        "bin/align/phyluce_align_get_gblocks_trimmed_alignments_from_untrimmed"
    )
    output = os.path.join(o_dir, "mafft-gblocks")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        expected_file = os.path.join(e_dir, "mafft-gblocks", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_trimal_trim(o_dir, e_dir, request):
    program = (
        "bin/align/phyluce_align_get_trimal_trimmed_alignments_from_untrimmed"
    )
    output = os.path.join(o_dir, "mafft-trimal")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        expected_file = os.path.join(e_dir, "mafft-trimal", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_edge_trim(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_get_trimmed_alignments_from_untrimmed"
    output = os.path.join(o_dir, "mafft-edge-trim")
    # note that thus only uses alignemnts with an odd
    # number of taxa so ties in base composition at a
    # column do not cause random differences in expected output
    # this also completes testing of generic_align and seqalign
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-for-edge-trim"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        print(name)
        expected_file = os.path.join(e_dir, "mafft-edge-trim", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_missing_data_designators(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_add_missing_data_designators"
    output = os.path.join(o_dir, "mafft-missing-data-designators")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--match-count-output",
        os.path.join(e_dir, "taxon-set.incomplete.conf"),
        "--incomplete-matrix",
        os.path.join(e_dir, "taxon-set.incomplete"),
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        print(name)
        expected_file = os.path.join(
            e_dir, "mafft-missing-data-designators", name
        )
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_convert_degen_bases(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_convert_degen_bases"
    output = os.path.join(o_dir, "mafft-degen-bases-converted")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-degen-bases"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        print(name)
        expected_file = os.path.join(
            e_dir, "mafft-degen-bases-converted", name
        )
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_convert_align_mafft_fasta_to_nexus(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_convert_one_align_to_another"
    output = os.path.join(o_dir, "mafft-fasta-to-nexus")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        expected_file = os.path.join(e_dir, "mafft-fasta-to-nexus", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_convert_align_mafft_fasta_to_phylip_relaxed(
    o_dir, e_dir, request
):
    program = "bin/align/phyluce_align_convert_one_align_to_another"
    output = os.path.join(o_dir, "mafft-fasta-to-phylip-relaxed")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--output-format",
        "phylip-relaxed",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        expected_file = os.path.join(
            e_dir, "mafft-fasta-to-phylip-relaxed", name
        )
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_convert_align_mafft_nexus_to_fasta(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_convert_one_align_to_another"
    output = os.path.join(o_dir, "mafft-nexus-to-fasta")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-fasta-to-nexus"),
        "--output",
        output,
        "--input-format",
        "nexus",
        "--output-format",
        "fasta",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        expected_file = os.path.join(e_dir, "mafft-nexus-to-fasta", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_explode_alignments_by_taxon(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_explode_alignments"
    output = os.path.join(o_dir, "mafft-exploded-by-taxon")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft"),
        "--output",
        output,
        "--input-format",
        "fasta",
        "--by-taxon",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        expected_file = os.path.join(e_dir, "mafft-exploded-by-taxon", name)
        observed = SeqIO.to_dict(SeqIO.parse(output_file, "fasta"))
        expected = SeqIO.to_dict(SeqIO.parse(expected_file, "fasta"))
        for name, observed in observed.items():
            assert expected[name].seq == observed.seq


def test_align_remove_locus_name(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_remove_locus_name_from_nexus_lines"
    output = os.path.join(o_dir, "mafft-gblocks-clean")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-gblocks"),
        "--output",
        output,
        "--input-format",
        "nexus",
        "--output-format",
        "nexus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        expected_file = os.path.join(e_dir, "mafft-gblocks-clean", name)
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_extract_taxa_from_alignments_exclude(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_extract_taxa_from_alignments"
    output = os.path.join(o_dir, "mafft-gblocks-clean-drop-gallus-gallus")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-gblocks-clean"),
        "--output",
        output,
        "--input-format",
        "nexus",
        "--output-format",
        "nexus",
        "--exclude",
        "gallus_gallus",
        "--cores",
        "1",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        expected_file = os.path.join(
            e_dir, "mafft-gblocks-clean-drop-gallus-gallus", name
        )
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_extract_taxa_from_alignments_include(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_extract_taxa_from_alignments"
    output = os.path.join(
        o_dir, "mafft-gblocks-clean-keep-gallus-and-peromyscus"
    )
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-gblocks-clean"),
        "--output",
        output,
        "--input-format",
        "nexus",
        "--output-format",
        "nexus",
        "--include",
        "gallus_gallus",
        "peromyscus_maniculatus",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    # pdb.set_trace()
    output_files = glob.glob(os.path.join(output, "*"))
    assert output_files, "There are no output files"
    for output_file in output_files:
        name = os.path.basename(output_file)
        expected_file = os.path.join(
            e_dir, "mafft-gblocks-clean-keep-gallus-and-peromyscus", name
        )
        observed = open(output_file).read()
        expected = open(expected_file).read()
        assert observed == expected


def test_align_extract_taxon_fasta_from_alignments(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_extract_taxon_fasta_from_alignments"
    output = os.path.join(o_dir, "mafft-gblocks-clean-gallus.fasta")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-gblocks-clean"),
        "--output",
        output,
        "--input-format",
        "nexus",
        "--taxon",
        "gallus_gallus",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    assert output, "There are is no output"
    expected_file = os.path.join(e_dir, "mafft-gblocks-clean-gallus.fasta")
    observed = SeqIO.to_dict(SeqIO.parse(output, "fasta"))
    expected = SeqIO.to_dict(SeqIO.parse(expected_file, "fasta"))
    for name, observed in observed.items():
        assert expected[name].seq == observed.seq


def test_align_filter_alignments(o_dir, e_dir, request):
    program = "bin/align/phyluce_align_filter_alignments"
    output = os.path.join(o_dir, "mafft-gblocks-filtered-alignments")
    cmd = [
        os.path.join(request.config.rootdir, program),
        "--alignments",
        os.path.join(e_dir, "mafft-gblocks-clean"),
        "--output",
        output,
        "--input-format",
        "nexus",
        "--containing-data-for",
        "gallus_gallus",
        "--min-length",
        "600",
        "--min-taxa",
        "3",
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    assert proc.returncode == 0, print("""{}""".format(stderr.decode("utf-8")))
    output_files = [
        os.path.basename(i) for i in glob.glob(os.path.join(output, "*"))
    ]
    assert output_files, "There are no output files"
    expected_files = [
        os.path.basename(i)
        for i in glob.glob(
            os.path.join(e_dir, "mafft-gblocks-filtered-alignments", "*")
        )
    ]
    assert set(output_files) == set(expected_files)
