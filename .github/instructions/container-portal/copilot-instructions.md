# Copilot Instructions - Core Container Portal

Este arquivo contém instruções e boas práticas para desenvolvimento neste repositório. Ele guia assistentes de IA (como Copilot) e desenvolvedores sobre convenções, padrões e fluxos do projeto.

---

## 📋 Visão Geral do Projeto

**Nome:** Core Container Portal  
**Tipo:** Container Module Federation (Webpack) - Integra múltiplos Microfrontends  
**Descrição:** Repositório do container responsável por orquestrar e integrar os microfrontends do portal de operações e franquia do Grupo Boticário.  
**Repositório:** https://github.com/grupoboticario/prodfin-pc-core-container-portal

### Características
- ✅ Ponto de entrada principal para portais de crédito
- ✅ Coordena navegação e estado global
- ✅ Gerencia versionamento de MFEs compartilhadas
- ✅ Fornece componentes base via Flora

---

## 🛠️ Stack Técnico

### Core
- **React:** v18 (com JSX runtime automático)
- **TypeScript:** ES2022 target, strict mode
- **Module Federation:** Webpack - orquestração de MFEs
- **Bundler:** Webpack 5 (configurações: dev, prod)

### Bibliotecas Principais
- **Flora:** Design system interno do GB (componentes reutilizáveis)
- **TanStack Query (React Query):** Gerenciamento de estado assíncrono e cache
- **Fetch API:** Requisições HTTP nativas (sem axios/node-fetch)
- **Husky:** Automação de tarefas via git hooks

### Qualidade de Código
- **ESLint:** Linting com Airbnb config + TypeScript plugin
- **Prettier:** Formatação automática
- **Jest:** Testes unitários e de integração
- **React Testing Library:** Testes de componentes (user-centric)

### Ambiente
- **Node.js:** v22 (obrigatório)
- **Package Manager:** Yarn v1 (⚠️ NÃO use npm)
- **OS Suportados:** macOS, Linux

---

## 📁 Estrutura do Projeto

```
prodfin-pc-core-container-portal/
├── src/
│   ├── components/          # Componentes React reutilizáveis
│   │   ├── Button/
│   │   │   ├── index.ts
│   │   │   ├── Button.tsx
│   │   │   ├── Button.styled.ts
│   │   │   └── Button.test.tsx
│   ├── pages/               # Páginas/rotas
│   ├── hooks/               # Custom hooks reutilizáveis
│   ├── services/            # Lógica de API e serviços
│   ├── constants/           # Constantes compartilhadas
│   ├── types/               # Tipos TypeScript globais
│   ├── utils/               # Funções utilitárias
│   ├── store/               # Estado global
│   ├── styles/              # Estilos globais
│   └── App.tsx
├── public/                  # Assets estáticos
├── webpack.*.js             # Configurações Webpack
├── package.json
├── tsconfig.json
└── .github/copilot-instructions.md
```

---

## 🚀 Scripts Disponíveis

### Desenvolvimento
| Script | Descrição |
| --- | --- |
| `yarn start` | Inicia dev server com hot reload (porta 3000) |
| `yarn build` | Build para desenvolvimento |
| `yarn build:prd` | Build otimizado para produção |
| `yarn serve` | Inicia servidor local |

### Qualidade de Código
| Script | Descrição |
| --- | --- |
| `yarn lint-check` | Verifica ESLint (máx 10 warnings) |
| `yarn lint-fix` | Corrige problemas ESLint automaticamente |
| `yarn prettier-check` | Verifica formatação Prettier |
| `yarn prettier-fix` | Formata código com Prettier |
| `yarn check-all` | Executa lint, prettier e testes |

### Testes
| Script | Descrição |
| --- | --- |
| `yarn test` | Executa testes (modo watch) |
| `yarn test:ci` | Testes com coverage para CI/CD |
| `yarn test:coverage` | Gera relatório de coverage |

---

## 🏗️ Convenções de Nomenclatura e Organização

### Nomenclatura de Arquivos e Pastas

#### Componentes (PascalCase)
```bash
# ✅ Correto
components/Button/Button.tsx
components/Button/Button.styled.ts
components/Button/Button.test.tsx

# ❌ Evitar
components/button/button.tsx
```

#### Hooks, Utilitários, Serviços (camelCase com sufixo)
```bash
# ✅ Correto
hooks/useLocalStorage.hook.ts
utils/date/date.util.ts
services/auth.service.ts

# ❌ Evitar
hooks/UseLocalStorage.ts
utils/date.ts
```

### Extensões de Arquivos Obrigatórias

| Tipo | Extensão | Exemplo |
|------|----------|---------|
| Constantes | `.constants.ts` | `api.constants.ts` |
| Testes | `.test.ts/tsx` | `Button.test.tsx` |
| Styled Components | `.styled.ts` | `Button.styled.ts` |
| Custom Hooks | `.hook.ts` | `useAuth.hook.ts` |
| Serviços | `.service.ts` | `auth.service.ts` |
| Utilitários | `.util.ts` | `date.util.ts` |
| Tipos | `.types.ts` ou `.d.ts` | `user.types.ts` |
| Stores | `.store.ts` | `app.store.ts` |

### Index.ts Pattern

**Apenas exportações, nunca implementação:**
```typescript
// ✅ Correto
// src/components/Button/index.ts
export { Button } from './Button';

// ❌ Evitar
export const Button = ({ ... }) => { ... };
```

---

## 📝 Convenções de Código

### TypeScript
- **Target:** ES2022
- **Modo Strict:** Ativado (obrigatório)
- Sempre tipifique props, estados e retornos
- Use interfaces para props de componentes

```typescript
// ✅ Correto
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ label, onClick, disabled }) => (
  <button onClick={onClick} disabled={disabled}>{label}</button>
);
```

### React 18 & JSX
- JSX runtime automático (sem import React)
- Functional components com named exports
- Respeite as regras dos hooks (ESLint enforcement)

```typescript
// ✅ Correto
export const MyComponent: React.FC<Props> = ({ prop }) => {
  const [value, setValue] = useState(null);
  
  useEffect(() => {
    // efeito aqui
  }, [value]); // sempre listar dependências
  
  return <div>{value}</div>;
};
```

### Importações
- Agrupe: React/libs → internas → types
- Use path aliases definidos em `tsconfig.json`
- Evite barrel imports em hot paths

```typescript
// ✅ Correto
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { Button } from 'components/Button';
import { useAuth } from 'hooks/useAuth.hook';

import type { User } from 'types/user';

// ❌ Evitar
import { Button } from '@components';
```

### Exportações

**Sempre exporte ao final do arquivo:**

```typescript
// ✅ Correto
const Button: React.FC<Props> = ({ label }) => <button>{label}</button>;

export { Button };
export type { Props };

// ❌ Evitar
export const Button: React.FC<Props> = ...
```

---

## 🧪 Padrões de Testes

### Setup
- **Framework:** Jest + React Testing Library
- **Coverage:** Mínimo 80% (enforced em CI/CD)
- **Approach:** User-centric (simule comportamento do usuário)

### Localização
- **Componentes:** `Component.test.tsx` no mesmo nível
- **Hooks:** `useHook.test.ts` no mesmo nível
- **Utilitários:** `util.test.ts` no mesmo nível

### Nomenclatura
- **Describe:** Nome do componente/função
- **It/Test:** Verbo 3ª pessoa singular: `renders`, `fetches`, `submits`

```typescript
// ✅ Correto
describe('Button', () => {
  it('renders button with label', () => {
    render(<Button label="Click" />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick} />);
    await userEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalled();
  });
});
```

### Queries - Prioridade

1. **`getByRole`** — Melhor acessibilidade e resiliência
2. **`getByLabelText`** — Para inputs
3. **`getByTestId`** — Último recurso

```typescript
// ✅ Correto
expect(screen.getByRole('button', { name: /click/i })).toBeInTheDocument();

// ❌ Evitar
screen.getByTestId('button');
```

---

## 🎯 Padrões Arquiteturais

### Module Federation (CRÍTICO)
- **Coordenação:** Sincronize dependências com todos os MFEs
- **Compartilhamento:** React, React-DOM, TanStack Query devem estar em comum
- **Testes:** Use `local-server.js` para testar integração MFE

### Data Fetching
- **TanStack Query:** Use para queries assíncronas com cache automático
- **Fetch API:** Nativa (não use axios)
- **Services:** Organize chamadas API em `src/services/`

```typescript
// ✅ Correto - TanStack Query
const useUsers = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(r => r.json())
  });
};
```

### State Management
- **Props Drilling:** Para estados simples
- **Context + useReducer:** Para estado global
- **TanStack Query:** Para cache server-side

---

## 🚨 Atenções Críticas

- ⚠️ **Yarn v1 apenas** — Não use npm
- ⚠️ **Module Federation:** Coordene versões compartilhadas
- ⚠️ **Sem secrets:** Não comita `.env.local` ou credentials
- ⚠️ **Coverage:** Mínimo 80% enforced em CI/CD
- ⚠️ **Husky:** Bloqueia commits que falham em lint/prettier/testes

---

## 📚 Recursos

- **Flora:** https://github.com/grupoboticario/flora
- **React 18:** https://react.dev/
- **TypeScript:** https://www.typescriptlang.org/docs/
- **TanStack Query:** https://tanstack.com/query/latest/
- **Webpack MF:** https://webpack.js.org/concepts/module-federation/

---

**Última atualização:** Abril 2026  
**Mantido por:** Grupo Boticário - Engineering Team
