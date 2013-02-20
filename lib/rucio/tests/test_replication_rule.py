# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2012-2013
# - Mario Lassnig, <mario.lassnig@cern.ch>, 2013

import re

from nose.tools import assert_is_instance, assert_regexp_matches

from rucio.client.dataidentifierclient import DataIdentifierClient
from rucio.client.replicationruleclient import ReplicationRuleClient
from rucio.client.rseclient import RSEClient
from rucio.client.scopeclient import ScopeClient
from rucio.common.utils import generate_uuid as uuid
from rucio.daemons.Conveyor import run_once as Conveyor_run


class TestIdentifierClients():

    def setup(self):
        self.did_client = DataIdentifierClient()
        self.rule_client = ReplicationRuleClient()
        self.rse_client = RSEClient()
        self.scope_client = ScopeClient()

    def test_add_replication_rule(self):
        """ REPLICATION RULE (CLIENT): Add a replication rule """

        # Add a scope
        tmp_scope = 'scope_%s' % uuid()[:22]
        self.scope_client.add_scope('root', tmp_scope)

        # Add a RSE
        tmp_rse = 'RSE_%s' % uuid()
        self.rse_client.add_rse(tmp_rse)

        # Add 10 Tiers1 RSEs
        for i in xrange(5):
            tmp_rse_t1 = 'RSE_%s' % uuid()
            self.rse_client.add_rse(tmp_rse_t1)
            self.rse_client.add_rse_attribute(rse=tmp_rse_t1, key='Tier', value='1')

        # Add datasets
        dsns = list()
        for i in xrange(5):
            tmp_dataset = 'dsn_' + str(uuid())
            # Add file replicas
            tmp_file = 'file_%s' % uuid()
            self.rse_client.add_file_replica(tmp_rse, tmp_scope, tmp_file, 1L, 1L)
            files = [{'scope': tmp_scope, 'name': tmp_file}, ]
            self.did_client.add_dataset(scope=tmp_scope, name=tmp_dataset)
            self.did_client.add_files_to_dataset(scope=tmp_scope, name=tmp_dataset, files=files)
            dsns.append({'scope': tmp_scope, 'name': tmp_dataset})

        ret = self.rule_client.add_replication_rule(dids=dsns, copies=2, rse_expression='Tier=1')
        assert_is_instance(ret, dict)
        assert_regexp_matches(ret['rule_id'], re.compile('^(\{){0,1}[0-9a-fA-F]{8}[0-9a-fA-F]{4}[0-9a-fA-F]{4}[0-9a-fA-F]{4}[0-9a-fA-F]{12}(\}){0,1}$'))

        Conveyor_run()
