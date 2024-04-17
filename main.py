# -*- coding: utf-8 -*-

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from alibabacloud_sts20150401.client import Client as Sts20150401Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_sts20150401 import models as sts_20150401_models
from alibabacloud_tea_util import models as util_models


class STS:
    def __init__(self,
                 access_key_id=None,
                 access_key_secret=None,
                 role_arn=None,
                 policy=None) -> None:
        """
        初始化
        :param access_key_id:
        :param access_key_secret:
        :param role_arn:
        """
        self.access_key_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID') if access_key_id is None else access_key_id
        self.access_key_secret = os.environ.get(
            'ALIBABA_CLOUD_ACCESS_KEY_SECRET') if access_key_secret is None else access_key_secret
        self.role_arn = os.environ.get('ROLE_ARN') if role_arn is None else role_arn
        self.policy = open("./policy/bucket_write_policy.txt").read() if policy is None else policy
        self.client = self.create_client()

    def create_client(self) -> Sts20150401Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
            endpoint="sts.cn-hangzhou.aliyuncs.com"
        )
        return Sts20150401Client(config)

    def get_token(self) -> None:
        assume_role_request = sts_20150401_models.AssumeRoleRequest(
            role_arn=self.role_arn,
            role_session_name="external-username",
            policy=self.policy
        )
        runtime = util_models.RuntimeOptions()
        try:
            res = self.client.assume_role_with_options(assume_role_request, runtime)
            if res.status_code == 200:
                return res.body.credentials
            else:
                raise RuntimeError("获取 sts token 接口返回不正常")
        except Exception as error:
            raise RuntimeError("创建 sts token 报错") from error

    async def get_token_async(self) -> None:
        assume_role_request = sts_20150401_models.AssumeRoleRequest(
            role_arn=self.role_arn,
            role_session_name="external-username",
            policy=self.policy
        )
        runtime = util_models.RuntimeOptions()
        try:
            res = await self.client.assume_role_with_options_async(assume_role_request, runtime)
            if res.status_code == 200:
                return res.body.credentials
            else:
                raise RuntimeError("获取 sts token 接口返回不正常")
        except Exception as error:
            raise RuntimeError("创建 sts token 报错") from error


app = FastAPI()

sts = STS()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)


@app.get('/')
async def read_root():
    results = await sts.get_token_async()
    return results
