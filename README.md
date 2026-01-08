# Mult-App - Kubernetes Deployment

Aplicação Python com Helm Chart para deploy em Kubernetes usando ArgoCD (GitOps).

## 📁 Estrutura do Repositório

```
mult-app/
├── multi-app/                    # Helm Chart
│   ├── Chart.yaml
│   ├── values.yaml              # Configuração base
│   ├── values-dev.yaml          # Configuração desenvolvimento
│   ├── values-prod.yaml         # Configuração produção
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       └── namespace.yaml
│
├── src/                          # Código da aplicação
│   └── app.py
│
├── Dockerfile                    # Build da imagem
└── .github/workflows/            # CI/CD (Build de imagens)
```

## 🚀 Deploy com ArgoCD

Este repositório está configurado para usar ArgoCD para deploy automático via GitOps.

### 1. Instalar ArgoCD

```bash
# Criar namespace
kubectl create namespace argocd

# Instalar ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Aguardar pods ficarem prontos
kubectl wait --for=condition=ready pod --all -n argocd --timeout=300s

# Obter senha inicial do admin
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### 2. Acessar ArgoCD UI

```bash
# Port-forward para acessar localmente
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Acesse: https://localhost:8080
# Usuário: admin
# Senha: (obtida no passo anterior)
```

### 3. Criar Application no ArgoCD

**Via CLI:**
```bash
argocd app create mult-app \
  --repo https://github.com/rcboufleur/mult-app.git \
  --path multi-app \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace nano \
  --values values.yaml
```

**Via YAML (Application Manifest):**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: mult-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/rcboufleur/mult-app.git
    targetRevision: main
    path: multi-app
    helm:
      valueFiles:
        - values.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: nano
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Aplique com:
```bash
kubectl apply -f argocd-app.yaml
```

### 4. Múltiplos Ambientes

Para diferentes ambientes, crie applications separadas:

**Desenvolvimento:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: mult-app-dev
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/rcboufleur/mult-app.git
    targetRevision: develop
    path: multi-app
    helm:
      valueFiles:
        - values-dev.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: nano-dev
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**Produção:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: mult-app-prod
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/rcboufleur/mult-app.git
    targetRevision: main
    path: multi-app
    helm:
      valueFiles:
        - values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: nano-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## 🔄 Fluxo de Trabalho

1. **Push no GitHub** → GitHub Actions faz build da imagem Docker
2. **ArgoCD detecta mudanças** no repositório Git
3. **ArgoCD faz sync automático** (se `automated: true`)
4. **Helm faz deploy** no cluster Kubernetes

## 📦 Build de Imagens

O GitHub Actions faz build automático das imagens Docker e publica no GitHub Container Registry (`ghcr.io/rcboufleur/mult-app`).

Para usar essas imagens, atualize os `values.yaml`:

```yaml
deployment:
  image:
    repository: ghcr.io/rcboufleur/mult-app
    tag: latest
    pullPolicy: Always
```

E configure o secret para autenticação:

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=rcboufleur \
  --docker-password=$GITHUB_TOKEN \
  --namespace nano
```

## 🔍 Verificar Deploy

```bash
# Ver aplicações no ArgoCD
argocd app list

# Ver status de uma aplicação
argocd app get mult-app

# Ver pods
kubectl get pods -n nano

# Ver serviços
kubectl get svc -n nano

# Ver logs
kubectl logs -f deployment/mult-app -n nano
```

## 📝 Configuração

As configurações podem ser ajustadas nos arquivos:
- `multi-app/values.yaml` - Base
- `multi-app/values-dev.yaml` - Desenvolvimento
- `multi-app/values-prod.yaml` - Produção

## 📚 Recursos

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

