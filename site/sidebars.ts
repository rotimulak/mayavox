import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  mainSidebar: [
    {
      type: 'doc',
      id: 'methodology',
      label: 'Методология анализа',
    },
    {
      type: 'doc',
      id: 'chat-participants',
      label: 'Участники чата',
    },
    {
      type: 'doc',
      id: 'projects',
      label: 'Проекты',
    },
    {
      type: 'doc',
      id: 'vision-evolution',
      label: 'Эволюция концепции',
    },
    {
      type: 'doc',
      id: 'positions-by-participant',
      label: 'Позиции участников',
    },
    {
      type: 'doc',
      id: 'positions-evolution',
      label: 'Хронология позиций',
    },
    {
      type: 'doc',
      id: 'positions-matrix',
      label: 'Матрица позиций',
    },
  ],
};

export default sidebars;
