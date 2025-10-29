{{/*
Expand the name of the chart.
*/}}
{{- define "ollama-intel.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "ollama-intel.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ollama-intel.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ollama-intel.labels" -}}
helm.sh/chart: {{ include "ollama-intel.chart" . }}
{{ include "ollama-intel.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ollama-intel.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ollama-intel.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Ollama component labels
*/}}
{{- define "ollama-intel.ollama.labels" -}}
{{ include "ollama-intel.labels" . }}
app.kubernetes.io/component: ollama
{{- end }}

{{/*
Ollama selector labels
*/}}
{{- define "ollama-intel.ollama.selectorLabels" -}}
{{ include "ollama-intel.selectorLabels" . }}
app.kubernetes.io/component: ollama
{{- end }}

{{/*
WebUI component labels
*/}}
{{- define "ollama-intel.webui.labels" -}}
{{ include "ollama-intel.labels" . }}
app.kubernetes.io/component: webui
{{- end }}

{{/*
WebUI selector labels
*/}}
{{- define "ollama-intel.webui.selectorLabels" -}}
{{ include "ollama-intel.selectorLabels" . }}
app.kubernetes.io/component: webui
{{- end }}

{{/*
Create the name of the ollama service
*/}}
{{- define "ollama-intel.ollama.serviceName" -}}
{{ include "ollama-intel.fullname" . }}-ollama
{{- end }}

{{/*
Create the name of the webui service
*/}}
{{- define "ollama-intel.webui.serviceName" -}}
{{ include "ollama-intel.fullname" . }}-webui
{{- end }}

{{/*
Llama.cpp component labels
*/}}
{{- define "ollama-intel.llamacpp.labels" -}}
{{ include "ollama-intel.labels" . }}
app.kubernetes.io/component: llamacpp
{{- end }}

{{/*
Llama.cpp selector labels
*/}}
{{- define "ollama-intel.llamacpp.selectorLabels" -}}
{{ include "ollama-intel.selectorLabels" . }}
app.kubernetes.io/component: llamacpp
{{- end }}

{{/*
Create the name of the llamacpp service
*/}}
{{- define "ollama-intel.llamacpp.serviceName" -}}
{{ include "ollama-intel.fullname" . }}-llamacpp
{{- end }}
