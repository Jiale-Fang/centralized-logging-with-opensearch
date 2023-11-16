/*
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
import React from "react";
import { SvcDetailProps } from "../ServiceLogDetail";
import LogProcessor from "pages/dataInjection/common/LogProcessor";
import { buildOSIPipelineNameByPipelineId, defaultStr } from "assets/js/utils";

const ServiceLogProcessor: React.FC<SvcDetailProps> = (
  props: SvcDetailProps
) => {
  const { pipelineInfo, amplifyConfig } = props;
  return (
    <LogProcessor
      amplifyConfig={amplifyConfig}
      osiParams={pipelineInfo?.osiParams}
      osiPipelineName={buildOSIPipelineNameByPipelineId(
        defaultStr(pipelineInfo?.id)
      )}
      processorLambda={pipelineInfo?.processorLambda}
    />
  );
};

export default ServiceLogProcessor;
